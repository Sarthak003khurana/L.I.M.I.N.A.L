import json
import random
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# INPUT / OUTPUT PATHS
# ============================================================

OLD_DATASET_DIR = (
    ROOT
    / "dataset"
    / "synthesizer"
)

V2_DATASET_DIR = (
    ROOT
    / "dataset"
    / "synthesizer_v2"
)

OLD_TRAIN_FILE = (
    OLD_DATASET_DIR
    / "train.jsonl"
)

OLD_VALIDATION_FILE = (
    OLD_DATASET_DIR
    / "validation.jsonl"
)

OLD_TEST_FILE = (
    OLD_DATASET_DIR
    / "test.jsonl"
)

NEW_FEATURE_FILE = (
    V2_DATASET_DIR
    / "new_contrastive_with_features.jsonl"
)

V2_TRAIN_FILE = (
    V2_DATASET_DIR
    / "train.jsonl"
)

V2_VALIDATION_FILE = (
    V2_DATASET_DIR
    / "validation.jsonl"
)

V2_TEST_FILE = (
    V2_DATASET_DIR
    / "test.jsonl"
)

MANIFEST_FILE = (
    V2_DATASET_DIR
    / "dataset_manifest.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

random.seed(SEED)


# ============================================================
# M5 LABELS
# ============================================================

SYNTHESIZER_LABELS = [

    "NO_SIGNIFICANT_OMISSION",

    "UNSTATED_PREFERENCE",

    "AVOIDING_COMMITMENT",

    "DISTANCING_FROM_RESPONSIBILITY",

    "EMOTIONAL_DISENGAGEMENT",

    "WITHHELD_CONTEXT",

    "UNSUPPORTED_REASONING",

    "AMBIGUOUS_INTENT",
]


LABEL_TO_ID = {
    label: index
    for index, label
    in enumerate(
        SYNTHESIZER_LABELS
    )
}


# ============================================================
# JSONL HELPERS
# ============================================================

def load_jsonl(path):

    records = []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if line:

                records.append(
                    json.loads(line)
                )

    return records


def save_jsonl(
    path,
    records
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )


# ============================================================
# NORMALIZE RECORD
# ============================================================

def normalize_record(
    record
):

    if "text" not in record:

        raise ValueError(
            "Record is missing 'text'."
        )

    if "label" not in record:

        raise ValueError(
            "Record is missing 'label'."
        )

    label = record["label"]

    if label not in LABEL_TO_ID:

        raise ValueError(
            f"Unknown M5 label: {label}"
        )

    if "features" not in record:

        raise ValueError(
            f"Record has no features: "
            f"{record['text']}"
        )

    features = record["features"]

    if len(features) != 25:

        raise ValueError(
            "M5 feature vector must contain "
            f"25 values, got {len(features)} "
            f"for: {record['text']}"
        )

    normalized = dict(record)

    normalized["text"] = (
        record["text"]
        .strip()
    )

    normalized["label_id"] = (
        LABEL_TO_ID[label]
    )

    normalized["target"] = label

    normalized["features"] = [
        float(value)
        for value in features
    ]

    return normalized


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

def get_distribution(
    records
):

    distribution = {
        label: 0
        for label in SYNTHESIZER_LABELS
    }

    for record in records:

        label = record["label"]

        if label in distribution:

            distribution[label] += 1

    return distribution


def print_distribution(
    title,
    records
):

    print(
        f"\n{title}"
    )

    print(
        "-" * 55
    )

    distribution = get_distribution(
        records
    )

    for label in SYNTHESIZER_LABELS:

        print(
            f"{label:<35}"
            f"{distribution[label]:>5}"
        )


# ============================================================
# VALIDATE UNIQUE TEXT
# ============================================================

def validate_unique_text(
    records,
    dataset_name
):

    texts = [
        record["text"]
        for record in records
    ]

    duplicates = (
        len(texts)
        - len(set(texts))
    )

    if duplicates > 0:

        raise ValueError(
            f"{dataset_name} contains "
            f"{duplicates} duplicate text entries."
        )


# ============================================================
# VALIDATE FAMILIES
# ============================================================

def validate_family_isolation(
    train_records,
    validation_records,
    test_records
):

    train_families = {
        record.get("family")
        for record in train_records
        if record.get("family") is not None
    }

    validation_families = {
        record.get("family")
        for record in validation_records
        if record.get("family") is not None
    }

    test_families = {
        record.get("family")
        for record in test_records
        if record.get("family") is not None
    }

    train_validation_overlap = (
        train_families
        & validation_families
    )

    train_test_overlap = (
        train_families
        & test_families
    )

    validation_test_overlap = (
        validation_families
        & test_families
    )

    if train_validation_overlap:

        raise ValueError(
            "Family leakage between "
            "train and validation:\n"
            f"{train_validation_overlap}"
        )

    if train_test_overlap:

        raise ValueError(
            "Family leakage between "
            "train and test:\n"
            f"{train_test_overlap}"
        )

    if validation_test_overlap:

        raise ValueError(
            "Family leakage between "
            "validation and test:\n"
            f"{validation_test_overlap}"
        )

    print(
        "\n✓ No family leakage detected."
    )


# ============================================================
# VALIDATE RECORD
# ============================================================

def validate_record(
    record
):

    required_fields = [
        "text",
        "features",
        "label",
        "label_id",
    ]

    for field in required_fields:

        if field not in record:

            raise ValueError(
                f"Missing field '{field}' "
                f"in record:\n{record}"
            )

    if len(record["features"]) != 25:

        raise ValueError(
            "Invalid feature count."
        )

    expected_id = LABEL_TO_ID[
        record["label"]
    ]

    if record["label_id"] != expected_id:

        raise ValueError(
            f"Incorrect label_id for "
            f"{record['label']}: "
            f"{record['label_id']} "
            f"!= {expected_id}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 70
    )

    print(
        "L.I.M.I.N.A.L. M5 V2 DATASET BUILDER"
    )

    print(
        "=" * 70
    )

    print(
        f"\nRandom seed: {SEED}"
    )

    # --------------------------------------------------------
    # Load original datasets
    # --------------------------------------------------------

    print(
        "\nLoading original dataset..."
    )

    old_train = load_jsonl(
        OLD_TRAIN_FILE
    )

    old_validation = load_jsonl(
        OLD_VALIDATION_FILE
    )

    old_test = load_jsonl(
        OLD_TEST_FILE
    )

    print(
        f"Original train      : "
        f"{len(old_train)}"
    )

    print(
        f"Original validation  : "
        f"{len(old_validation)}"
    )

    print(
        f"Original blind test  : "
        f"{len(old_test)}"
    )

    # --------------------------------------------------------
    # Load new examples
    # --------------------------------------------------------

    print(
        "\nLoading new contrastive examples..."
    )

    new_examples = load_jsonl(
        NEW_FEATURE_FILE
    )

    print(
        f"New examples         : "
        f"{len(new_examples)}"
    )

    if len(new_examples) != 166:

        raise ValueError(
            "Expected exactly 166 new "
            f"examples, got {len(new_examples)}."
        )

    # --------------------------------------------------------
    # Normalize everything
    # --------------------------------------------------------

    old_train = [
        normalize_record(record)
        for record in old_train
    ]

    old_validation = [
        normalize_record(record)
        for record in old_validation
    ]

    old_test = [
        normalize_record(record)
        for record in old_test
    ]

    new_examples = [
        normalize_record(record)
        for record in new_examples
    ]

    print(
        "\n✓ All records normalized."
    )

    # --------------------------------------------------------
    # Validate original blind test
    # --------------------------------------------------------

    original_test_snapshot = [
        json.dumps(
            record,
            sort_keys=True
        )
        for record in old_test
    ]

    # --------------------------------------------------------
    # Show distributions
    # --------------------------------------------------------

    print_distribution(
        "Original TRAIN distribution",
        old_train
    )

    print_distribution(
        "Original VALIDATION distribution",
        old_validation
    )

    print_distribution(
        "New examples distribution",
        new_examples
    )

    # --------------------------------------------------------
    # Separate new examples by class
    # --------------------------------------------------------

    new_by_class = {
        label: []
        for label in SYNTHESIZER_LABELS
    }

    for record in new_examples:

        new_by_class[
            record["label"]
        ].append(
            record
        )

    # --------------------------------------------------------
    # Split new examples
    #
    # We use 80% for train and 20% for validation.
    #
    # IMPORTANT:
    # The original train/validation family separation
    # remains untouched.
    # --------------------------------------------------------

    new_train = []

    new_validation = []

    print(
        "\nSplitting new examples..."
    )

    for label in SYNTHESIZER_LABELS:

        class_examples = (
            new_by_class[label]
        )

        random.shuffle(
            class_examples
        )

        total = len(
            class_examples
        )

        train_count = int(
            total * 0.80
        )

        class_train = (
            class_examples[
                :train_count
            ]
        )

        class_validation = (
            class_examples[
                train_count:
            ]
        )

        new_train.extend(
            class_train
        )

        new_validation.extend(
            class_validation
        )

        print(
            f"{label:<35}"
            f"total={total:>3} "
            f"train={len(class_train):>3} "
            f"val={len(class_validation):>3}"
        )

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    v2_train = (
        old_train
        + new_train
    )

    v2_validation = (
        old_validation
        + new_validation
    )

    # CRITICAL:
    # Blind test is copied exactly.
    v2_test = list(
        old_test
    )

    # --------------------------------------------------------
    # Shuffle train / validation
    # --------------------------------------------------------

    random.shuffle(
        v2_train
    )

    random.shuffle(
        v2_validation
    )

    # --------------------------------------------------------
    # Validate every record
    # --------------------------------------------------------

    print(
        "\nValidating records..."
    )

    for record in v2_train:

        validate_record(
            record
        )

    for record in v2_validation:

        validate_record(
            record
        )

    for record in v2_test:

        validate_record(
            record
        )

    print(
        "✓ Every record has 25 features."
    )

    print(
        "✓ Every record has a valid label_id."
    )

    # --------------------------------------------------------
    # Validate text uniqueness inside splits
    # --------------------------------------------------------

    validate_unique_text(
        v2_train,
        "TRAIN"
    )

    validate_unique_text(
        v2_validation,
        "VALIDATION"
    )

    validate_unique_text(
        v2_test,
        "TEST"
    )

    print(
        "✓ No duplicate text inside any split."
    )

    # --------------------------------------------------------
    # Validate cross-split text leakage
    # --------------------------------------------------------

    train_texts = {
        record["text"]
        for record in v2_train
    }

    validation_texts = {
        record["text"]
        for record in v2_validation
    }

    test_texts = {
        record["text"]
        for record in v2_test
    }

    if train_texts & validation_texts:

        raise ValueError(
            "Text leakage between "
            "train and validation."
        )

    if train_texts & test_texts:

        raise ValueError(
            "Text leakage between "
            "train and test."
        )

    if validation_texts & test_texts:

        raise ValueError(
            "Text leakage between "
            "validation and test."
        )

    print(
        "✓ No text leakage detected."
    )

    # --------------------------------------------------------
    # Validate family isolation
    # --------------------------------------------------------

    validate_family_isolation(
        v2_train,
        v2_validation,
        v2_test
    )

    # --------------------------------------------------------
    # Verify blind test is unchanged
    # --------------------------------------------------------

    new_test_snapshot = [
        json.dumps(
            record,
            sort_keys=True
        )
        for record in v2_test
    ]

    if (
        original_test_snapshot
        != new_test_snapshot
    ):

        raise RuntimeError(
            "CRITICAL: Blind test was modified."
        )

    print(
        "✓ Blind test remains completely unchanged."
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    print(
        "\nSaving M5 V2 datasets..."
    )

    save_jsonl(
        V2_TRAIN_FILE,
        v2_train
    )

    save_jsonl(
        V2_VALIDATION_FILE,
        v2_validation
    )

    save_jsonl(
        V2_TEST_FILE,
        v2_test
    )

    # --------------------------------------------------------
    # Manifest
    # --------------------------------------------------------

    manifest = {

        "dataset_version":
            "M5_V2_TARGETED_CONTRASTIVE",

        "random_seed":
            SEED,

        "num_classes":
            len(SYNTHESIZER_LABELS),

        "features_per_example":
            25,

        "original_train":
            len(old_train),

        "original_validation":
            len(old_validation),

        "new_examples":
            len(new_examples),

        "new_train":
            len(new_train),

        "new_validation":
            len(new_validation),

        "final_train":
            len(v2_train),

        "final_validation":
            len(v2_validation),

        "final_test":
            len(v2_test),

        "test_preserved":
            True,

        "labels":
            {
                label: LABEL_TO_ID[label]
                for label in SYNTHESIZER_LABELS
            },

        "train_distribution":
            get_distribution(
                v2_train
            ),

        "validation_distribution":
            get_distribution(
                v2_validation
            ),

        "test_distribution":
            get_distribution(
                v2_test
            ),

        "new_examples_distribution":
            get_distribution(
                new_examples
            ),
    }

    with open(
        MANIFEST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            manifest,
            file,
            indent=2
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "M5 V2 DATASET BUILD COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nFinal train       : "
        f"{len(v2_train)}"
    )

    print(
        f"Final validation  : "
        f"{len(v2_validation)}"
    )

    print(
        f"Blind test        : "
        f"{len(v2_test)}"
    )

    print(
        f"Total             : "
        f"{len(v2_train) + len(v2_validation) + len(v2_test)}"
    )

    print(
        "\nFinal TRAIN distribution:"
    )

    for label, count in (
        get_distribution(
            v2_train
        ).items()
    ):

        print(
            f"  {label:<35}"
            f"{count}"
        )

    print(
        "\nFinal VALIDATION distribution:"
    )

    for label, count in (
        get_distribution(
            v2_validation
        ).items()
    ):

        print(
            f"  {label:<35}"
            f"{count}"
        )

    print(
        "\nFinal TEST distribution:"
    )

    for label, count in (
        get_distribution(
            v2_test
        ).items()
    ):

        print(
            f"  {label:<35}"
            f"{count}"
        )

    print(
        "\nFiles created:"
    )

    print(
        f"  {V2_TRAIN_FILE}"
    )

    print(
        f"  {V2_VALIDATION_FILE}"
    )

    print(
        f"  {V2_TEST_FILE}"
    )

    print(
        f"  {MANIFEST_FILE}"
    )

    print(
        "\n✓ M5 test set was NOT changed."
    )

    print(
        "✓ M5 test set remains blind."
    )

    print(
        "✓ Dataset is ready for V2 training."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()