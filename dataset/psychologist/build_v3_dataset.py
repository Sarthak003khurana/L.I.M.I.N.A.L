import json
import random
import re
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "psychologist"
    / "psychologist_v2.jsonl"
)

OUTPUT_DIR = (
    BASE_DIR
    / "dataset"
    / "psychologist"
)

TRAIN_FILE = (
    OUTPUT_DIR
    / "psychologist_v3_train.jsonl"
)

VALIDATION_FILE = (
    OUTPUT_DIR
    / "psychologist_v3_validation.jsonl"
)

TEST_FILE = (
    OUTPUT_DIR
    / "psychologist_v3_test.jsonl"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "psychologist_v3_report.json"
)

SEED = 42

random.seed(SEED)


LABELS = [
    "NO_AFFECT_SIGNAL",
    "AFFECT_GAP",
    "FORCED_POLITENESS",
    "EMOTIONAL_INCONGRUENCE",
    "DISENGAGEMENT_SIGNAL",
    "RESENTMENT_SIGNAL",
    "EMOTIONAL_AVOIDANCE",
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    text = text.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# FAMILY SIGNATURE
# ============================================================

def family_signature(text):

    text = normalize_text(text)

    # Remove punctuation
    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    words = text.split()

    # Remove common function words so sentences with
    # the same underlying template are grouped together.
    stop_words = {
        "i",
        "we",
        "they",
        "he",
        "she",
        "it",
        "the",
        "a",
        "an",
        "is",
        "am",
        "are",
        "was",
        "were",
        "to",
        "of",
        "and",
        "but",
        "for",
        "with",
        "about",
        "this",
        "that",
        "my",
        "your",
        "do",
        "not",
        "really",
        "very",
        "just",
    }

    filtered = [
        word
        for word in words
        if word not in stop_words
    ]

    # Use sorted content words as a coarse family signature.
    return " ".join(
        sorted(filtered)
    )


# ============================================================
# LOAD DATA
# ============================================================

def load_examples():

    examples = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            if line.strip():

                examples.append(
                    json.loads(line)
                )

    return examples


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

def remove_exact_duplicates(examples):

    unique = {}

    for example in examples:

        text = normalize_text(
            example["text"]
        )

        labels = tuple(
            sorted(example["labels"])
        )

        key = (
            text,
            labels
        )

        if key not in unique:

            unique[key] = example

    return list(
        unique.values()
    )


# ============================================================
# GROUP BY FAMILY
# ============================================================

def create_families(examples):

    families = {}

    for example in examples:

        signature = family_signature(
            example["text"]
        )

        if signature not in families:

            families[signature] = []

        families[signature].append(
            example
        )

    return families


# ============================================================
# STRATIFIED SPLIT
# ============================================================

def split_dataset(examples):

    random.shuffle(
        examples
    )

    # We first assign examples to splits while trying to
    # maintain label distribution.

    train = []
    validation = []
    test = []

    label_examples = {
        label: []
        for label in LABELS
    }

    for example in examples:

        for label in example["labels"]:

            label_examples[label].append(
                example
            )

    assigned = set()

    # --------------------------------------------------------
    # First pass: distribute each label
    # --------------------------------------------------------

    for label in LABELS:

        items = label_examples[label]

        random.shuffle(items)

        n = len(items)

        test_count = max(
            1,
            round(n * 0.15)
        )

        validation_count = max(
            1,
            round(n * 0.15)
        )

        test_items = items[
            :test_count
        ]

        validation_items = items[
            test_count:
            test_count + validation_count
        ]

        train_items = items[
            test_count + validation_count:
        ]

        for item in test_items:

            key = normalize_text(
                item["text"]
            )

            if key not in assigned:

                test.append(item)
                assigned.add(key)

        for item in validation_items:

            key = normalize_text(
                item["text"]
            )

            if key not in assigned:

                validation.append(item)
                assigned.add(key)

        for item in train_items:

            key = normalize_text(
                item["text"]
            )

            if key not in assigned:

                train.append(item)
                assigned.add(key)

    # --------------------------------------------------------
    # Make sure every example is assigned
    # --------------------------------------------------------

    all_keys = {
        normalize_text(
            item["text"]
        )
        for item in examples
    }

    assigned_keys = {
        normalize_text(
            item["text"]
        )
        for item in (
            train
            + validation
            + test
        )
    }

    remaining = [
        item
        for item in examples
        if normalize_text(
            item["text"]
        ) not in assigned_keys
    ]

    random.shuffle(
        remaining
    )

    for item in remaining:

        if len(train) <= len(examples) * 0.70:

            train.append(item)

        elif len(validation) <= len(examples) * 0.15:

            validation.append(item)

        else:

            test.append(item)

    return (
        train,
        validation,
        test
    )


# ============================================================
# WRITE JSONL
# ============================================================

def write_jsonl(
    path,
    examples
):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        for example in examples:

            f.write(
                json.dumps(
                    example,
                    ensure_ascii=False
                )
                + "\n"
            )


# ============================================================
# LABEL DISTRIBUTION
# ============================================================

def label_distribution(examples):

    counts = Counter()

    for example in examples:

        for label in example["labels"]:

            counts[label] += 1

    return {
        label: counts[label]
        for label in LABELS
    }


# ============================================================
# LEAKAGE CHECK
# ============================================================

def check_exact_leakage(
    first,
    second
):

    first_texts = {
        normalize_text(
            item["text"]
        )
        for item in first
    }

    second_texts = {
        normalize_text(
            item["text"]
        )
        for item in second
    }

    return len(
        first_texts
        & second_texts
    )


def check_family_leakage(
    first,
    second
):

    first_families = {
        family_signature(
            item["text"]
        )
        for item in first
    }

    second_families = {
        family_signature(
            item["text"]
        )
        for item in second
    }

    return len(
        first_families
        & second_families
    )


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 70)
    print(
        "L.I.M.I.N.A.L. — "
        "PSYCHOLOGIST V3 DATASET BUILDER"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    examples = load_examples()

    print(
        f"\nLoaded examples: "
        f"{len(examples)}"
    )

    # --------------------------------------------------------
    # Remove exact duplicates
    # --------------------------------------------------------

    examples = remove_exact_duplicates(
        examples
    )

    print(
        f"After exact deduplication: "
        f"{len(examples)}"
    )

    # --------------------------------------------------------
    # Family statistics
    # --------------------------------------------------------

    families = create_families(
        examples
    )

    print(
        f"Unique families: "
        f"{len(families)}"
    )

    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    train, validation, test = (
        split_dataset(examples)
    )

    # --------------------------------------------------------
    # Shuffle each split
    # --------------------------------------------------------

    random.shuffle(train)
    random.shuffle(validation)
    random.shuffle(test)

    # --------------------------------------------------------
    # Write
    # --------------------------------------------------------

    write_jsonl(
        TRAIN_FILE,
        train
    )

    write_jsonl(
        VALIDATION_FILE,
        validation
    )

    write_jsonl(
        TEST_FILE,
        test
    )

    # --------------------------------------------------------
    # Distributions
    # --------------------------------------------------------

    train_distribution = (
        label_distribution(train)
    )

    validation_distribution = (
        label_distribution(validation)
    )

    test_distribution = (
        label_distribution(test)
    )

    # --------------------------------------------------------
    # Leakage
    # --------------------------------------------------------

    exact_train_validation = (
        check_exact_leakage(
            train,
            validation
        )
    )

    exact_train_test = (
        check_exact_leakage(
            train,
            test
        )
    )

    exact_validation_test = (
        check_exact_leakage(
            validation,
            test
        )
    )

    family_train_validation = (
        check_family_leakage(
            train,
            validation
        )
    )

    family_train_test = (
        check_family_leakage(
            train,
            test
        )
    )

    family_validation_test = (
        check_family_leakage(
            validation,
            test
        )
    )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    report = {

        "total_examples": len(examples),

        "split_sizes": {
            "train": len(train),
            "validation": len(validation),
            "test": len(test),
        },

        "label_distribution": {

            "train": train_distribution,

            "validation":
                validation_distribution,

            "test":
                test_distribution,
        },

        "leakage": {

            "exact": {

                "train_validation":
                    exact_train_validation,

                "train_test":
                    exact_train_test,

                "validation_test":
                    exact_validation_test,
            },

            "family": {

                "train_validation":
                    family_train_validation,

                "train_test":
                    family_train_test,

                "validation_test":
                    family_validation_test,
            },
        },

        "seed": SEED,
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=2
        )

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "SPLIT RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTrain       : "
        f"{len(train)} "
        f"({len(train) / len(examples) * 100:.1f}%)"
    )

    print(
        f"Validation  : "
        f"{len(validation)} "
        f"({len(validation) / len(examples) * 100:.1f}%)"
    )

    print(
        f"Test        : "
        f"{len(test)} "
        f"({len(test) / len(examples) * 100:.1f}%)"
    )

    # --------------------------------------------------------
    # Label table
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "LABEL DISTRIBUTION"
    )

    print(
        "=" * 70
    )

    print(
        f"\n{'LABEL':30}"
        f"{'TRAIN':>10}"
        f"{'VAL':>10}"
        f"{'TEST':>10}"
    )

    print(
        "-" * 60
    )

    for label in LABELS:

        print(
            f"{label:30}"
            f"{train_distribution[label]:>10}"
            f"{validation_distribution[label]:>10}"
            f"{test_distribution[label]:>10}"
        )

    # --------------------------------------------------------
    # Leakage report
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "EXACT DUPLICATE LEAKAGE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTrain / Validation : "
        f"{exact_train_validation}"
    )

    print(
        f"Train / Test       : "
        f"{exact_train_test}"
    )

    print(
        f"Validation / Test  : "
        f"{exact_validation_test}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "FAMILY LEAKAGE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTrain / Validation : "
        f"{family_train_validation}"
    )

    print(
        f"Train / Test       : "
        f"{family_train_test}"
    )

    print(
        f"Validation / Test  : "
        f"{family_validation_test}"
    )

    # --------------------------------------------------------
    # Files
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "FILES CREATED"
    )

    print(
        "=" * 70
    )

    print(
        f"\n{TRAIN_FILE}"
    )

    print(
        f"{VALIDATION_FILE}"
    )

    print(
        f"{TEST_FILE}"
    )

    print(
        f"{REPORT_FILE}"
    )

    print(
        "\nV3 dataset construction complete."
    )


if __name__ == "__main__":

    main()