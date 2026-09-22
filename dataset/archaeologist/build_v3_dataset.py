import json
import random
import re
from pathlib import Path
from collections import Counter, defaultdict

SEED = 42
random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "archaeologist_v2.jsonl"

TRAIN_FILE = BASE_DIR / "archaeologist_v3_train.jsonl"
VALIDATION_FILE = BASE_DIR / "archaeologist_v3_validation.jsonl"
TEST_FILE = BASE_DIR / "archaeologist_v3_test.jsonl"

REPORT_FILE = BASE_DIR / "archaeologist_v3_report.json"

LABELS = [
    "NO_OMISSION",
    "HEDGING",
    "MISSING_ACTOR",
    "PASSIVE_CONSTRUCTION",
    "MISSING_COMMITMENT",
    "VAGUE_REFERENCE",
    "RESPONSIBILITY_AVOIDANCE",
]


# ============================================================
# LOAD
# ============================================================

def load_jsonl(path):
    data = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                data.append(json.loads(line))

    return data


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):
    text = text.lower().strip()

    text = re.sub(r"\s+", " ", text)

    return text


def tokenize(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text.lower())


# ============================================================
# EXACT DUPLICATE REMOVAL
# ============================================================

def remove_exact_duplicates(data):

    unique = {}
    duplicates = 0

    for example in data:

        text = normalize_text(example["text"])

        labels = tuple(
            sorted(
                set(example.get("labels", []))
            )
        )

        key = (text, labels)

        if key in unique:
            duplicates += 1
            continue

        example["text"] = example["text"].strip()
        example["labels"] = list(labels)

        unique[key] = example

    return list(unique.values()), duplicates


# ============================================================
# TEMPLATE / FAMILY SIGNATURE
#
# This catches examples that differ only by names,
# numbers, times, or other obvious generated variables.
# ============================================================

NAMES = {
    "sarah",
    "james",
    "rahul",
    "priya",
    "john",
}

VARIABLE_WORDS = {
    "yesterday",
    "today",
    "tomorrow",
    "tonight",
    "morning",
    "afternoon",
    "evening",
    "friday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "saturday",
    "sunday",
    "sometime",
    "eventually",
    "later",
    "soon",
    "today",
}


def family_signature(text):

    tokens = tokenize(text)

    signature = []

    for token in tokens:

        if token in NAMES:
            signature.append("<NAME>")

        elif token.isdigit():
            signature.append("<NUMBER>")

        elif token in VARIABLE_WORDS:
            signature.append("<TIME>")

        else:
            signature.append(token)

    return " ".join(signature)


# ============================================================
# GROUP DATA BY FAMILY
# ============================================================

def build_families(data):

    families = defaultdict(list)

    for example in data:

        signature = family_signature(
            example["text"]
        )

        families[signature].append(example)

    return families


# ============================================================
# MULTI-LABEL KEY
# ============================================================

def label_key(example):

    return tuple(
        sorted(
            set(example.get("labels", []))
        )
    )


# ============================================================
# GROUP-BASED SPLIT
#
# Families never cross train/validation/test.
#
# Target:
# 80% train
# 10% validation
# 10% test
# ============================================================

def split_families(families):

    family_items = list(families.items())

    random.shuffle(family_items)

    # Larger families first after shuffle.
    family_items.sort(
        key=lambda item: len(item[1]),
        reverse=True,
    )

    total_examples = sum(
        len(examples)
        for _, examples in family_items
    )

    target_train = int(total_examples * 0.80)
    target_validation = int(total_examples * 0.10)

    train = []
    validation = []
    test = []

    train_count = 0
    validation_count = 0

    for _, examples in family_items:

        family_size = len(examples)

        if train_count + family_size <= target_train:
            train.extend(examples)
            train_count += family_size

        elif validation_count + family_size <= target_validation:
            validation.extend(examples)
            validation_count += family_size

        else:
            test.extend(examples)

    # Safety: if one of the splits is empty, rebalance.
    if len(validation) == 0 and len(train) > 0:

        move_count = max(
            1,
            len(train) // 10
        )

        validation = train[-move_count:]
        train = train[:-move_count]

    if len(test) == 0 and len(train) > 0:

        move_count = max(
            1,
            len(train) // 10
        )

        test = train[-move_count:]
        train = train[:-move_count]

    random.shuffle(train)
    random.shuffle(validation)
    random.shuffle(test)

    return train, validation, test


# ============================================================
# CHECK EXACT OVERLAP
# ============================================================

def exact_overlap(a, b):

    a_text = {
        normalize_text(x["text"])
        for x in a
    }

    b_text = {
        normalize_text(x["text"])
        for x in b
    }

    return a_text.intersection(b_text)


# ============================================================
# CHECK FAMILY OVERLAP
# ============================================================

def family_overlap(a, b):

    a_families = {
        family_signature(x["text"])
        for x in a
    }

    b_families = {
        family_signature(x["text"])
        for x in b
    }

    return a_families.intersection(b_families)


# ============================================================
# LABEL COUNTS
# ============================================================

def count_labels(data):

    counts = Counter()

    for example in data:

        for label in example.get("labels", []):

            counts[label] += 1

    return {
        label: counts[label]
        for label in LABELS
    }


# ============================================================
# MULTI-LABEL STATISTICS
# ============================================================

def count_multilabel(data):

    return sum(
        1
        for example in data
        if len(example.get("labels", [])) > 1
    )


# ============================================================
# WRITE JSONL
# ============================================================

def write_jsonl(path, data):

    with open(path, "w", encoding="utf-8") as file:

        for example in data:

            file.write(
                json.dumps(
                    example,
                    ensure_ascii=False,
                )
                + "\n"
            )


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("L.I.M.I.N.A.L. — ARCHAEOLOGIST V3 DATASET BUILDER")
print("=" * 70)

print()
print("Input:")
print(INPUT_FILE)

if not INPUT_FILE.exists():

    print()
    print("ERROR: Input dataset does not exist.")
    print()
    print("Expected:")
    print(INPUT_FILE)

    raise SystemExit(1)


# ------------------------------------------------------------
# Load
# ------------------------------------------------------------

data = load_jsonl(INPUT_FILE)

print()
print(f"Loaded examples : {len(data)}")


# ------------------------------------------------------------
# Exact deduplication
# ------------------------------------------------------------

data, duplicate_count = remove_exact_duplicates(data)

print(
    f"Duplicates removed : {duplicate_count}"
)

print(
    f"Unique examples    : {len(data)}"
)


# ------------------------------------------------------------
# Build families
# ------------------------------------------------------------

families = build_families(data)

print(
    f"Unique families    : {len(families)}"
)


# ------------------------------------------------------------
# Split
# ------------------------------------------------------------

train, validation, test = split_families(
    families
)


# ------------------------------------------------------------
# Leakage checks
# ------------------------------------------------------------

train_val_exact = exact_overlap(
    train,
    validation
)

train_test_exact = exact_overlap(
    train,
    test
)

validation_test_exact = exact_overlap(
    validation,
    test
)

train_val_family = family_overlap(
    train,
    validation
)

train_test_family = family_overlap(
    train,
    test
)

validation_test_family = family_overlap(
    validation,
    test
)


# ------------------------------------------------------------
# Counts
# ------------------------------------------------------------

train_labels = count_labels(train)
validation_labels = count_labels(validation)
test_labels = count_labels(test)


# ------------------------------------------------------------
# Print results
# ------------------------------------------------------------

print()
print("=" * 70)
print("V3 SPLIT")
print("=" * 70)

print()
print(
    f"Train        : {len(train)} "
    f"({len(train) / len(data) * 100:.1f}%)"
)

print(
    f"Validation   : {len(validation)} "
    f"({len(validation) / len(data) * 100:.1f}%)"
)

print(
    f"Test         : {len(test)} "
    f"({len(test) / len(data) * 100:.1f}%)"
)


print()
print("Label distribution:")
print("-" * 70)

print(
    f"{'LABEL':<28}"
    f"{'TRAIN':>10}"
    f"{'VAL':>10}"
    f"{'TEST':>10}"
)

print("-" * 70)

for label in LABELS:

    print(
        f"{label:<28}"
        f"{train_labels[label]:>10}"
        f"{validation_labels[label]:>10}"
        f"{test_labels[label]:>10}"
    )


# ------------------------------------------------------------
# Multi-label count
# ------------------------------------------------------------

print()
print("Multi-label examples:")

print(
    f"Train      : {count_multilabel(train)}"
)

print(
    f"Validation : {count_multilabel(validation)}"
)

print(
    f"Test       : {count_multilabel(test)}"
)


# ------------------------------------------------------------
# Leakage report
# ------------------------------------------------------------

print()
print("=" * 70)
print("LEAKAGE CHECK")
print("=" * 70)

print()
print(
    f"Exact Train/Validation overlap : "
    f"{len(train_val_exact)}"
)

print(
    f"Exact Train/Test overlap       : "
    f"{len(train_test_exact)}"
)

print(
    f"Exact Validation/Test overlap  : "
    f"{len(validation_test_exact)}"
)

print()
print(
    f"Family Train/Validation overlap : "
    f"{len(train_val_family)}"
)

print(
    f"Family Train/Test overlap       : "
    f"{len(train_test_family)}"
)

print(
    f"Family Validation/Test overlap  : "
    f"{len(validation_test_family)}"
)


# ------------------------------------------------------------
# Write datasets
# ------------------------------------------------------------

write_jsonl(
    TRAIN_FILE,
    train,
)

write_jsonl(
    VALIDATION_FILE,
    validation,
)

write_jsonl(
    TEST_FILE,
    test,
)


# ------------------------------------------------------------
# Report
# ------------------------------------------------------------

report = {
    "seed": SEED,
    "input_examples": len(data),
    "duplicates_removed": duplicate_count,
    "unique_families": len(families),
    "splits": {
        "train": len(train),
        "validation": len(validation),
        "test": len(test),
    },
    "labels": LABELS,
    "label_distribution": {
        "train": train_labels,
        "validation": validation_labels,
        "test": test_labels,
    },
    "multilabel_examples": {
        "train": count_multilabel(train),
        "validation": count_multilabel(validation),
        "test": count_multilabel(test),
    },
    "leakage": {
        "exact_train_validation": len(train_val_exact),
        "exact_train_test": len(train_test_exact),
        "exact_validation_test": len(validation_test_exact),
        "family_train_validation": len(train_val_family),
        "family_train_test": len(train_test_family),
        "family_validation_test": len(validation_test_family),
    },
}

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        report,
        file,
        indent=2,
        ensure_ascii=False,
    )


# ------------------------------------------------------------
# Final status
# ------------------------------------------------------------

print()
print("=" * 70)
print("FILES CREATED")
print("=" * 70)

print()
print(TRAIN_FILE)
print(VALIDATION_FILE)
print(TEST_FILE)
print(REPORT_FILE)

print()
print("=" * 70)
print("ARCHAEOLOGIST V3 COMPLETE")
print("=" * 70)