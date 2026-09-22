import json
import random
import re
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = (
    BASE_DIR
    / "dataset"
    / "psychologist"
)

TRAIN_FILE = (
    DATASET_DIR
    / "psychologist_v3_train.jsonl"
)

VALIDATION_FILE = (
    DATASET_DIR
    / "psychologist_v3_validation.jsonl"
)

TEST_FILE = (
    DATASET_DIR
    / "psychologist_v3_test.jsonl"
)

REPORT_FILE = (
    DATASET_DIR
    / "psychologist_v3_report.json"
)

SEED = 42

random.seed(SEED)


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

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    words = text.split()

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

    return " ".join(
        sorted(filtered)
    )


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(path):

    examples = []

    with open(
        path,
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
# FIND FAMILY LEAKAGE
# ============================================================

def find_family_leakage(
    train,
    validation,
    test
):

    train_families = {}

    validation_families = {}

    test_families = {}

    for example in train:

        signature = family_signature(
            example["text"]
        )

        train_families.setdefault(
            signature,
            []
        ).append(example)

    for example in validation:

        signature = family_signature(
            example["text"]
        )

        validation_families.setdefault(
            signature,
            []
        ).append(example)

    for example in test:

        signature = family_signature(
            example["text"]
        )

        test_families.setdefault(
            signature,
            []
        ).append(example)

    train_validation = (
        set(train_families)
        & set(validation_families)
    )

    train_test = (
        set(train_families)
        & set(test_families)
    )

    validation_test = (
        set(validation_families)
        & set(test_families)
    )

    return (
        train_families,
        validation_families,
        test_families,
        train_validation,
        train_test,
        validation_test,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "L.I.M.I.N.A.L. — "
        "PSYCHOLOGIST LEAKAGE FIX"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    train = load_jsonl(
        TRAIN_FILE
    )

    validation = load_jsonl(
        VALIDATION_FILE
    )

    test = load_jsonl(
        TEST_FILE
    )

    print(
        f"\nOriginal split:"
    )

    print(
        f"Train      : {len(train)}"
    )

    print(
        f"Validation : {len(validation)}"
    )

    print(
        f"Test       : {len(test)}"
    )

    # --------------------------------------------------------
    # Find leakage
    # --------------------------------------------------------

    (
        train_families,
        validation_families,
        test_families,
        train_validation,
        train_test,
        validation_test,
    ) = find_family_leakage(
        train,
        validation,
        test
    )

    print(
        "\nFamily overlap before fixing:"
    )

    print(
        f"Train / Validation : "
        f"{len(train_validation)}"
    )

    print(
        f"Train / Test       : "
        f"{len(train_test)}"
    )

    print(
        f"Validation / Test  : "
        f"{len(validation_test)}"
    )

    # --------------------------------------------------------
    # Collect problematic examples
    # --------------------------------------------------------

    leaked_examples = []

    for signature in train_validation:

        leaked_examples.extend(
            validation_families[
                signature
            ]
        )

    for signature in train_test:

        leaked_examples.extend(
            test_families[
                signature
            ]
        )

    # --------------------------------------------------------
    # Remove duplicates by normalized text
    # --------------------------------------------------------

    seen = set()

    unique_leaked = []

    for example in leaked_examples:

        key = normalize_text(
            example["text"]
        )

        if key not in seen:

            seen.add(key)

            unique_leaked.append(
                example
            )

    # --------------------------------------------------------
    # Remove leaked examples from validation/test
    # --------------------------------------------------------

    leaked_keys = {
        normalize_text(
            example["text"]
        )
        for example in unique_leaked
    }

    new_validation = [
        example
        for example in validation
        if normalize_text(
            example["text"]
        ) not in leaked_keys
    ]

    new_test = [
        example
        for example in test
        if normalize_text(
            example["text"]
        ) not in leaked_keys
    ]

    # --------------------------------------------------------
    # Put removed examples into training
    # --------------------------------------------------------

    new_train = (
        train
        + unique_leaked
    )

    random.shuffle(
        new_train
    )

    random.shuffle(
        new_validation
    )

    random.shuffle(
        new_test
    )

    # --------------------------------------------------------
    # Write corrected splits
    # --------------------------------------------------------

    write_jsonl(
        TRAIN_FILE,
        new_train
    )

    write_jsonl(
        VALIDATION_FILE,
        new_validation
    )

    write_jsonl(
        TEST_FILE,
        new_test
    )

    # --------------------------------------------------------
    # Verify leakage again
    # --------------------------------------------------------

    (
        _,
        _,
        _,
        final_train_validation,
        final_train_test,
        final_validation_test,
    ) = find_family_leakage(
        new_train,
        new_validation,
        new_test
    )

    # --------------------------------------------------------
    # Update report
    # --------------------------------------------------------

    report = {

        "total_examples": (
            len(new_train)
            + len(new_validation)
            + len(new_test)
        ),

        "split_sizes": {
            "train": len(new_train),
            "validation": len(new_validation),
            "test": len(new_test),
        },

        "family_leakage": {
            "train_validation":
                len(final_train_validation),

            "train_test":
                len(final_train_test),

            "validation_test":
                len(final_validation_test),
        },

        "removed_from_validation_test":
            len(unique_leaked),

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
    # Results
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "CORRECTED SPLIT"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTrain      : {len(new_train)}"
    )

    print(
        f"Validation : {len(new_validation)}"
    )

    print(
        f"Test       : {len(new_test)}"
    )

    print(
        f"\nMoved into training: "
        f"{len(unique_leaked)}"
    )

    print(
        "\nFamily leakage after fixing:"
    )

    print(
        f"Train / Validation : "
        f"{len(final_train_validation)}"
    )

    print(
        f"Train / Test       : "
        f"{len(final_train_test)}"
    )

    print(
        f"Validation / Test  : "
        f"{len(final_validation_test)}"
    )

    print(
        "\nCorrected V3 dataset saved."
    )


if __name__ == "__main__":

    main()