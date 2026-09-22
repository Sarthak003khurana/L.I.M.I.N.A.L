import json
import random
from pathlib import Path

# ============================================================
# L.I.M.I.N.A.L.
# ARCHAEOLOGIST — SEED DATASET GENERATOR
# ============================================================

SEED = 42
random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent

TRAIN_FILE = BASE_DIR / "archaeologist_train.jsonl"
VAL_FILE = BASE_DIR / "archaeologist_validation.jsonl"
TEST_FILE = BASE_DIR / "archaeologist_test.jsonl"


# ============================================================
# LABELS
# ============================================================

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
# SEED EXAMPLES
# ============================================================

examples = [

    # ========================================================
    # NO OMISSION
    # ========================================================

    {
        "text": "I will submit the report by Friday.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "Sarah approved the proposal yesterday.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "The engineering team will deploy the update tonight.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "I disagree with the proposed timeline.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "We decided to postpone the meeting until Monday.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "John will contact the client tomorrow morning.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "I completed the assignment this afternoon.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "The manager rejected the request.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "I do not agree with the proposed change.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "We will review the document tomorrow.",
        "labels": ["NO_OMISSION"]
    },


    # ========================================================
    # HEDGING
    # ========================================================

    {
        "text": "I guess we could maybe consider that option.",
        "labels": ["HEDGING"]
    },
    {
        "text": "Perhaps we should wait a little longer.",
        "labels": ["HEDGING"]
    },
    {
        "text": "It might be better to discuss this later.",
        "labels": ["HEDGING"]
    },
    {
        "text": "I suppose that could work.",
        "labels": ["HEDGING"]
    },
    {
        "text": "Maybe we can try something different.",
        "labels": ["HEDGING"]
    },
    {
        "text": "This is probably not the right approach.",
        "labels": ["HEDGING"]
    },
    {
        "text": "We could possibly revisit the issue next week.",
        "labels": ["HEDGING"]
    },
    {
        "text": "I am not entirely sure this will work.",
        "labels": ["HEDGING"]
    },
    {
        "text": "Perhaps that would be acceptable.",
        "labels": ["HEDGING"]
    },
    {
        "text": "It seems like we might need another option.",
        "labels": ["HEDGING"]
    },


    # ========================================================
    # MISSING ACTOR
    # ========================================================

    {
        "text": "Someone should probably handle this.",
        "labels": ["MISSING_ACTOR"]
    },
    {
        "text": "People are saying the project is delayed.",
        "labels": ["MISSING_ACTOR"]
    },
    {
        "text": "Apparently, someone changed the configuration.",
        "labels": ["MISSING_ACTOR"]
    },
    {
        "text": "They say the deadline has changed.",
        "labels": ["MISSING_ACTOR"]
    },
    {
        "text": "Everyone knows that the system failed.",
        "labels": ["MISSING_ACTOR"]
    },
    {
        "text": "Someone approved the request.",
        "labels": ["MISSING_ACTOR"]
    },
    {
        "text": "The team says that the problem is resolved.",
        "labels": ["NO_OMISSION"]
    },


    # ========================================================
    # PASSIVE CONSTRUCTION
    # ========================================================

    {
        "text": "The decision was made yesterday.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR"
        ]
    },
    {
        "text": "The report was submitted this morning.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR"
        ]
    },
    {
        "text": "The issue was discussed during the meeting.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR"
        ]
    },
    {
        "text": "The mistake was identified later.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR"
        ]
    },
    {
        "text": "The files were deleted accidentally.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR"
        ]
    },
    {
        "text": "The payment was processed yesterday.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR"
        ]
    },
    {
        "text": "The changes were approved without explanation.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR"
        ]
    },

    # Passive WITH explicit actor = hard negative for missing actor

    {
        "text": "The report was submitted by Sarah.",
        "labels": ["PASSIVE_CONSTRUCTION"]
    },
    {
        "text": "The proposal was approved by the manager.",
        "labels": ["PASSIVE_CONSTRUCTION"]
    },
    {
        "text": "The files were deleted by the administrator.",
        "labels": ["PASSIVE_CONSTRUCTION"]
    },
    {
        "text": "The payment was processed by the finance team.",
        "labels": ["PASSIVE_CONSTRUCTION"]
    },


    # ========================================================
    # MISSING COMMITMENT
    # ========================================================

    {
        "text": "We should probably look into it sometime.",
        "labels": ["MISSING_COMMITMENT"]
    },
    {
        "text": "I will think about it.",
        "labels": ["MISSING_COMMITMENT"]
    },
    {
        "text": "Something should be done about this.",
        "labels": ["MISSING_COMMITMENT"]
    },
    {
        "text": "We can deal with that later.",
        "labels": ["MISSING_COMMITMENT"]
    },
    {
        "text": "Let's see how things go.",
        "labels": ["MISSING_COMMITMENT"]
    },
    {
        "text": "I will get back to you at some point.",
        "labels": ["MISSING_COMMITMENT"]
    },
    {
        "text": "We should discuss this eventually.",
        "labels": ["MISSING_COMMITMENT"]
    },
    {
        "text": "Someone should take care of it eventually.",
        "labels": ["MISSING_COMMITMENT"]
    },


    # ========================================================
    # VAGUE REFERENCE
    # ========================================================

    {
        "text": "We should handle that thing soon.",
        "labels": ["VAGUE_REFERENCE"]
    },
    {
        "text": "That issue from before still needs attention.",
        "labels": ["VAGUE_REFERENCE"]
    },
    {
        "text": "You know what happened last time.",
        "labels": ["VAGUE_REFERENCE"]
    },
    {
        "text": "We need to fix it somehow.",
        "labels": ["VAGUE_REFERENCE"]
    },
    {
        "text": "Let's discuss that later.",
        "labels": ["VAGUE_REFERENCE"]
    },
    {
        "text": "Something about the project seems wrong.",
        "labels": ["VAGUE_REFERENCE"]
    },
    {
        "text": "That should probably be taken care of.",
        "labels": ["VAGUE_REFERENCE"]
    },


    # ========================================================
    # RESPONSIBILITY AVOIDANCE
    # ========================================================

    {
        "text": "I was only following what everyone else was doing.",
        "labels": ["RESPONSIBILITY_AVOIDANCE"]
    },
    {
        "text": "It was not really my decision.",
        "labels": ["RESPONSIBILITY_AVOIDANCE"]
    },
    {
        "text": "I just did what I was told.",
        "labels": ["RESPONSIBILITY_AVOIDANCE"]
    },
    {
        "text": "There was nothing I could really do.",
        "labels": ["RESPONSIBILITY_AVOIDANCE"]
    },
    {
        "text": "That was decided before I got involved.",
        "labels": ["RESPONSIBILITY_AVOIDANCE"]
    },
    {
        "text": "I cannot be blamed for what happened.",
        "labels": ["RESPONSIBILITY_AVOIDANCE"]
    },


    # ========================================================
    # MULTI-LABEL EXAMPLES
    # ========================================================

    {
        "text": "The decision was apparently made without further discussion.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR",
            "HEDGING"
        ]
    },
    {
        "text": "Maybe the issue will be handled somehow.",
        "labels": [
            "HEDGING",
            "VAGUE_REFERENCE",
            "MISSING_COMMITMENT"
        ]
    },
    {
        "text": "It was decided that someone should probably deal with it.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR",
            "HEDGING",
            "VAGUE_REFERENCE",
            "MISSING_COMMITMENT"
        ]
    },
    {
        "text": "I guess they decided to change it.",
        "labels": [
            "HEDGING",
            "MISSING_ACTOR",
            "VAGUE_REFERENCE"
        ]
    },
    {
        "text": "Something was done, but I was not involved in that decision.",
        "labels": [
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR",
            "VAGUE_REFERENCE",
            "RESPONSIBILITY_AVOIDANCE"
        ]
    },
    {
        "text": "The decision might be changed later by someone.",
        "labels": [
            "HEDGING",
            "PASSIVE_CONSTRUCTION",
            "MISSING_ACTOR",
            "MISSING_COMMITMENT"
        ]
    },


    # ========================================================
    # HARD NEGATIVES
    # ========================================================

    {
        "text": "The manager clearly explained the decision.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "Sarah will complete the task tomorrow.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "The report was written by James and submitted on Friday.",
        "labels": ["PASSIVE_CONSTRUCTION"]
    },
    {
        "text": "The team completed the project successfully.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "I will handle the issue personally.",
        "labels": ["NO_OMISSION"]
    },
    {
        "text": "We will meet with the client at three o'clock.",
        "labels": ["NO_OMISSION"]
    },
]


# ============================================================
# VALIDATION
# ============================================================

def validate_example(example):

    if "text" not in example:
        return False

    if "labels" not in example:
        return False

    if not isinstance(example["text"], str):
        return False

    if not example["text"].strip():
        return False

    if not isinstance(example["labels"], list):
        return False

    if not example["labels"]:
        return False

    for label in example["labels"]:

        if label not in LABELS:
            return False

    return True


for example in examples:

    if not validate_example(example):
        raise ValueError(
            f"Invalid dataset example:\n{example}"
        )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

unique_examples = {}

for example in examples:

    key = example["text"].strip().lower()

    unique_examples[key] = {
        "text": example["text"].strip(),
        "labels": example["labels"]
    }


examples = list(unique_examples.values())


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(examples)


# ============================================================
# SPLIT
# ============================================================

total = len(examples)

train_end = int(total * 0.70)
validation_end = int(total * 0.85)

train_data = examples[:train_end]

validation_data = examples[
    train_end:validation_end
]

test_data = examples[
    validation_end:
]


# ============================================================
# WRITE JSONL
# ============================================================

def write_jsonl(path, data):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        for example in data:

            file.write(
                json.dumps(
                    example,
                    ensure_ascii=False
                ) + "\n"
            )


write_jsonl(
    TRAIN_FILE,
    train_data
)

write_jsonl(
    VAL_FILE,
    validation_data
)

write_jsonl(
    TEST_FILE,
    test_data
)


# ============================================================
# LABEL STATISTICS
# ============================================================

label_counts = {
    label: 0
    for label in LABELS
}

for example in examples:

    for label in example["labels"]:

        label_counts[label] += 1


# ============================================================
# REPORT
# ============================================================

print("=" * 60)
print("L.I.M.I.N.A.L. ARCHAEOLOGIST SEED DATASET")
print("=" * 60)

print()

print(f"Total examples      : {total}")
print(f"Training examples   : {len(train_data)}")
print(f"Validation examples : {len(validation_data)}")
print(f"Test examples       : {len(test_data)}")

print()

print("Label distribution:")
print("-" * 60)

for label in LABELS:

    print(
        f"{label:<28} : {label_counts[label]}"
    )

print()

print("Files created:")

print(
    TRAIN_FILE
)

print(
    VAL_FILE
)

print(
    TEST_FILE
)

print()

print("Dataset generation complete.")