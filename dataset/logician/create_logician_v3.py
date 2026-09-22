import json
import random
from pathlib import Path
from collections import defaultdict, Counter

INPUT = Path("dataset/logician/logician_expanded.jsonl")
OUTPUT = Path("dataset/logician/logician_v3")

TRAIN_OUT = OUTPUT / "train.jsonl"
VAL_OUT = OUTPUT / "val.jsonl"
TEST_OUT = OUTPUT / "test.jsonl"

SEED = 42

LABELS = [
    "SKIPPED_PREMISE",
    "UNANSWERED_COUNTERARGUMENT",
    "UNSUPPORTED_CONCLUSION",
    "UNSTATED_ASSUMPTION",
    "CONTRADICTION",
    "FALSE_DILEMMA"
]


def normalize(text):
    return " ".join(text.lower().split())


def get_family(text):
    """
    The expansion script changes words/prefixes/suffixes.
    We recover the family using the stable core structure.
    """

    text = normalize(text)

    prefixes = [
        "clearly, ",
        "obviously, ",
        "according to the discussion, ",
        "the manager argues that ",
        "the report claims that ",
        "the team believes that ",
        "the proposal suggests that ",
        "in the meeting, they stated that ",
        "the analysis concludes that "
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break

    suffixes = [
        " this seems reasonable.",
        " that is why we should proceed.",
        " therefore, the decision is obvious.",
        " for that reason, the team should agree.",
        " this is presented as sufficient evidence."
    ]

    for suffix in suffixes:
        if text.endswith(suffix):
            text = text[:-len(suffix)]
            break

    # Normalize common substitutions back into a family signature.
    replacements = {
        "initiative": "project",
        "program": "project",
        "implementation": "project",

        "recommendation": "proposal",
        "approach": "proposal",
        "plan": "proposal",

        "group": "team",
        "department": "team",
        "staff": "team",

        "organization": "company",
        "business": "company",
        "firm": "company",

        "application": "product",
        "system": "product",
        "service": "product",

        "supervisor": "manager",
        "lead": "manager",
        "director": "manager",

        "worker": "employee",
        "staff member": "employee",
        "team member": "employee",

        "analysis": "report",
        "document": "report",
        "review": "report",

        "choice": "decision",
        "conclusion": "decision",
        "determination": "decision",

        "customers": "users",
        "clients": "users",
        "people": "users",

        "buyers": "users"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def build_families(examples):
    families = defaultdict(list)

    for item in examples:
        fid = get_family(item["text"])
        families[fid].append(item)

    return list(families.values())


def family_label_counts(family):
    counts = Counter()

    for item in family:
        for label in item["labels"]:
            counts[label] += 1

    return counts


def score_split(split, family):

    current = Counter()

    for item in split:
        for label in item["labels"]:
            current[label] += 1

    family_counts = family_label_counts(family)

    # Prefer adding a family to the split where its labels
    # are currently underrepresented.
    score = 0

    for label in LABELS:
        score += max(
            0,
            family_counts[label] * 3 - current[label]
        )

    return score


def stratified_split(families):

    random.seed(SEED)

    # Shuffle first.
    families = families.copy()
    random.shuffle(families)

    # Put larger / multi-label families first.
    families.sort(
        key=lambda x: (
            len(x),
            len(set(
                label
                for item in x
                for label in item["labels"]
            ))
        ),
        reverse=True
    )

    total = sum(len(f) for f in families)

    train_target = int(total * 0.80)
    val_target = int(total * 0.10)

    train = []
    val = []
    test = []

    # Process families one by one.
    for family in families:

        candidates = []

        # Calculate target distance and label balance.
        for name, split in [
            ("train", train),
            ("val", val),
            ("test", test)
        ]:

            current_size = len(split)

            if name == "train":
                target = train_target
            elif name == "val":
                target = val_target
            else:
                target = total - train_target - val_target

            size_penalty = abs(
                (current_size + len(family)) - target
            )

            label_bonus = score_split(split, family)

            # Strongly prioritize label balance,
            # then target size.
            score = label_bonus * 10 - size_penalty

            candidates.append(
                (score, name)
            )

        candidates.sort(reverse=True)

        selected = candidates[0][1]

        if selected == "train":
            train.extend(family)
        elif selected == "val":
            val.extend(family)
        else:
            test.extend(family)

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    return train, val, test


def print_distribution(name, data):

    counter = Counter()

    for item in data:
        for label in item["labels"]:
            counter[label] += 1

    negatives = sum(
        len(item["labels"]) == 0
        for item in data
    )

    multi = sum(
        len(item["labels"]) > 1
        for item in data
    )

    print(f"\n{name}: {len(data)} examples")

    for label in LABELS:
        print(
            f"  {label:28} {counter[label]}"
        )

    print(f"  {'MULTI_LABEL':28} {multi}")
    print(f"  {'HARD_NEGATIVES':28} {negatives}")


def main():

    print("=" * 60)
    print("M3 LOGICIAN STRATIFIED V3 SPLIT")
    print("=" * 60)

    examples = []

    with INPUT.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                examples.append(json.loads(line))

    print(f"Loaded examples: {len(examples)}")

    # Exact deduplication.
    unique = {}

    for item in examples:
        key = normalize(item["text"])

        if key not in unique:
            unique[key] = item

    examples = list(unique.values())

    print(
        f"After exact deduplication: {len(examples)}"
    )

    families = build_families(examples)

    print(
        f"Unique families: {len(families)}"
    )

    train, val, test = stratified_split(families)

    OUTPUT.mkdir(parents=True, exist_ok=True)

    def write_jsonl(path, data):

        with path.open(
            "w",
            encoding="utf-8"
        ) as f:

            for item in data:
                f.write(
                    json.dumps(
                        item,
                        ensure_ascii=False
                    ) + "\n"
                )

    write_jsonl(TRAIN_OUT, train)
    write_jsonl(VAL_OUT, val)
    write_jsonl(TEST_OUT, test)

    print_distribution("TRAIN", train)
    print_distribution("VALIDATION", val)
    print_distribution("TEST", test)

    # -------------------------
    # Exact leakage
    # -------------------------

    train_texts = {
        normalize(x["text"])
        for x in train
    }

    val_texts = {
        normalize(x["text"])
        for x in val
    }

    test_texts = {
        normalize(x["text"])
        for x in test
    }

    print("\nExact text leakage:")

    print(
        f"  Train / Val : "
        f"{len(train_texts & val_texts)}"
    )

    print(
        f"  Train / Test: "
        f"{len(train_texts & test_texts)}"
    )

    print(
        f"  Val / Test  : "
        f"{len(val_texts & test_texts)}"
    )

    # -------------------------
    # Family leakage
    # -------------------------

    train_families = {
        get_family(x["text"])
        for x in train
    }

    val_families = {
        get_family(x["text"])
        for x in val
    }

    test_families = {
        get_family(x["text"])
        for x in test
    }

    print("\nFamily leakage:")

    print(
        f"  Train / Val : "
        f"{len(train_families & val_families)}"
    )

    print(
        f"  Train / Test: "
        f"{len(train_families & test_families)}"
    )

    print(
        f"  Val / Test  : "
        f"{len(val_families & test_families)}"
    )

    print("\nSaved:")

    print(f"  {TRAIN_OUT}")
    print(f"  {VAL_OUT}")
    print(f"  {TEST_OUT}")

    print("=" * 60)


if __name__ == "__main__":
    main()
