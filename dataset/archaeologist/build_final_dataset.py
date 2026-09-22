import json
import random
import re
from pathlib import Path

# ============================================================
# L.I.M.I.N.A.L.
# ARCHAEOLOGIST — FINAL DATASET BUILDER
# ============================================================

SEED = 42
random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent

SEED_FILES = [
    BASE_DIR / "archaeologist_train.jsonl",
    BASE_DIR / "archaeologist_validation.jsonl",
    BASE_DIR / "archaeologist_test.jsonl",
]

EXPANDED_FILE = BASE_DIR / "archaeologist_expanded.jsonl"

FINAL_FILE = BASE_DIR / "archaeologist_final.jsonl"

TRAIN_FILE = BASE_DIR / "archaeologist_final_train.jsonl"

VAL_FILE = BASE_DIR / "archaeologist_final_validation.jsonl"

TEST_FILE = BASE_DIR / "archaeologist_final_test.jsonl"


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
# ADDITIONAL RESPONSIBILITY AVOIDANCE DATA
# ============================================================

RESPONSIBILITY_TEMPLATES = [

    "I only followed the instructions I received.",
    "That decision was made by someone else.",
    "I was not the person responsible for that decision.",
    "I simply followed the process that was provided.",
    "The manager told me to do it that way.",
    "I had no say in the final decision.",
    "That was outside my responsibility.",
    "I was only carrying out someone else's instructions.",
    "The team decided that without asking me.",
    "I did what I was asked to do.",
    "I was not involved in making that decision.",
    "The final decision was not mine.",
    "I had no control over that part of the project.",
    "Someone else was handling that issue.",
    "I was only responsible for my assigned part.",
    "That was already decided before I joined the project.",
    "I cannot take responsibility for that decision.",
    "I was following the instructions from my supervisor.",
    "The department made that decision.",
    "That issue was handled by another team.",
    "I did not have authority over that decision.",
    "I was not given control of that process.",
    "The decision came from management.",
    "I simply followed what the team had agreed.",
    "I had no involvement in choosing that option.",
    "The instructions came from above.",
    "I was acting according to the procedure.",
    "Another person was responsible for approving it.",
    "I was not authorized to make that decision.",
    "The client made the final call.",
    "That choice was made before I became involved.",
    "I was only executing the assigned task.",
    "I had no authority to change the outcome.",
    "Someone else gave me the instructions.",
    "The decision was outside my role.",
    "I was following the team's direction.",
    "I did not decide how the issue was handled.",
    "The supervisor made that call.",
    "I was not responsible for approving the request.",
    "The process was already defined when I started.",
    "I had no control over the final outcome.",
    "The project lead made the decision.",
    "I was only doing what the procedure required.",
    "That responsibility belonged to another department.",
    "I was not consulted before the decision was made.",
    "I had no authority to approve the change.",
    "The instructions were given to me by the manager.",
    "I did not choose the final approach.",
    "Someone else decided how we would proceed.",
]


# ============================================================
# HARD NEGATIVES
# ============================================================

RESPONSIBILITY_NEGATIVES = [

    "I made the decision after reviewing all the evidence.",
    "I approved the request myself.",
    "I chose the final approach for the project.",
    "I accepted responsibility for the mistake.",
    "I decided to change the schedule.",
    "I personally handled the issue.",
    "I authorized the deployment.",
    "I reviewed the problem and fixed it.",
    "I take full responsibility for the outcome.",
    "I decided how the task should be completed.",
]


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(path):

    data = []

    if not path.exists():
        return data

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if line:
                data.append(json.loads(line))

    return data


# ============================================================
# NORMALIZE
# ============================================================

def normalize(text):

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# CREATE EXAMPLE
# ============================================================

def create_example(
    text,
    labels,
    source_type,
    difficulty
):

    return {
        "text": normalize(text),
        "labels": sorted(set(labels)),
        "source_type": source_type,
        "difficulty": difficulty,
    }


# ============================================================
# LOAD ALL SEED DATA
# ============================================================

all_seed_data = []

for file_path in SEED_FILES:

    all_seed_data.extend(
        load_jsonl(file_path)
    )


expanded_data = load_jsonl(
    EXPANDED_FILE
)


# ============================================================
# COMBINE DATA
# ============================================================

combined = []


for example in all_seed_data:

    combined.append(
        create_example(
            example["text"],
            example["labels"],
            "human_seed",
            "medium",
        )
    )


for example in expanded_data:

    combined.append(
        create_example(
            example["text"],
            example["labels"],
            example.get(
                "source_type",
                "controlled_generation"
            ),
            example.get(
                "difficulty",
                "medium"
            ),
        )
    )


# ============================================================
# ADD RESPONSIBILITY AVOIDANCE
# ============================================================

for text in RESPONSIBILITY_TEMPLATES:

    combined.append(
        create_example(
            text,
            ["RESPONSIBILITY_AVOIDANCE"],
            "responsibility_generation",
            "medium",
        )
    )


# ============================================================
# ADD RESPONSIBILITY HARD NEGATIVES
# ============================================================

for text in RESPONSIBILITY_NEGATIVES:

    combined.append(
        create_example(
            text,
            ["NO_OMISSION"],
            "hard_negative",
            "hard",
        )
    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

unique = {}

for example in combined:

    key = (
        example["text"].lower(),
        tuple(example["labels"])
    )

    if key not in unique:

        unique[key] = example


combined = list(unique.values())


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(combined)


# ============================================================
# LABEL COUNTS
# ============================================================

label_counts = {
    label: 0
    for label in LABELS
}

for example in combined:

    for label in example["labels"]:

        label_counts[label] += 1


# ============================================================
# PRINT CURRENT DISTRIBUTION
# ============================================================

print("=" * 60)
print("CURRENT DATASET")
print("=" * 60)

print()

print(
    f"Total examples : {len(combined)}"
)

print()

for label in LABELS:

    print(
        f"{label:<28} : {label_counts[label]}"
    )


# ============================================================
# BALANCE TARGET
# ============================================================

TARGET_PER_LABEL = 250


# ============================================================
# GROUP EXAMPLES BY LABEL
# ============================================================

by_label = {
    label: []
    for label in LABELS
}

for example in combined:

    for label in example["labels"]:

        by_label[label].append(example)


# ============================================================
# BALANCE DATASET
# ============================================================

balanced = []

used = set()


for label in LABELS:

    candidates = by_label[label].copy()

    random.shuffle(candidates)

    count = 0

    for example in candidates:

        key = (
            example["text"].lower(),
            tuple(example["labels"])
        )

        if key in used:
            continue

        balanced.append(example)

        used.add(key)

        count += 1

        if count >= TARGET_PER_LABEL:
            break


# ============================================================
# ADD REMAINING EXAMPLES
# ============================================================

remaining = []

for example in combined:

    key = (
        example["text"].lower(),
        tuple(example["labels"])
    )

    if key not in used:

        remaining.append(example)


random.shuffle(remaining)


for example in remaining:

    if len(balanced) >= 2500:
        break

    balanced.append(example)


# ============================================================
# FINAL SHUFFLE
# ============================================================

random.shuffle(balanced)


# ============================================================
# FINAL SPLIT
# ============================================================

total = len(balanced)

train_end = int(total * 0.80)

val_end = int(total * 0.90)

train_data = balanced[:train_end]

validation_data = balanced[
    train_end:val_end
]

test_data = balanced[
    val_end:
]


# ============================================================
# SAVE FUNCTION
# ============================================================

def save_jsonl(path, data):

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


# ============================================================
# SAVE FINAL DATA
# ============================================================

save_jsonl(
    FINAL_FILE,
    balanced
)

save_jsonl(
    TRAIN_FILE,
    train_data
)

save_jsonl(
    VAL_FILE,
    validation_data
)

save_jsonl(
    TEST_FILE,
    test_data
)


# ============================================================
# FINAL DISTRIBUTION
# ============================================================

final_counts = {
    label: 0
    for label in LABELS
}

for example in balanced:

    for label in example["labels"]:

        final_counts[label] += 1


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 60)
print("FINAL ARCHAEOLOGIST DATASET")
print("=" * 60)

print()

print(
    f"Total examples      : {len(balanced)}"
)

print(
    f"Training examples   : {len(train_data)}"
)

print(
    f"Validation examples : {len(validation_data)}"
)

print(
    f"Test examples       : {len(test_data)}"
)

print()

print("Final label distribution:")
print("-" * 60)

for label in LABELS:

    print(
        f"{label:<28} : {final_counts[label]}"
    )

print()

print("Files created:")

print(FINAL_FILE)

print(TRAIN_FILE)

print(VAL_FILE)

print(TEST_FILE)

print()

print("FINAL DATASET BUILD COMPLETE.")