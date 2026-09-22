import json
import random
from pathlib import Path
from collections import Counter

INPUT = Path("dataset/logician/logician_seeds.jsonl")
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

PREFIXES = [
    "",
    "Clearly, ",
    "Obviously, ",
    "According to the discussion, ",
    "The manager argues that ",
    "The report claims that ",
    "The team believes that ",
    "The proposal suggests that ",
    "In the meeting, they stated that ",
    "The analysis concludes that "
]

SUFFIXES = [
    "",
    ".",
    " This seems reasonable.",
    " That is why we should proceed.",
    " Therefore, the decision is obvious.",
    " For that reason, the team should agree.",
    " This is presented as sufficient evidence."
]

SUBSTITUTIONS = {
    "project": ["project", "initiative", "program", "implementation"],
    "proposal": ["proposal", "plan", "recommendation", "approach"],
    "team": ["team", "group", "department", "staff"],
    "company": ["company", "organization", "business", "firm"],
    "product": ["product", "system", "application", "service"],
    "manager": ["manager", "supervisor", "lead", "director"],
    "employee": ["employee", "worker", "staff member", "team member"],
    "report": ["report", "analysis", "document", "review"],
    "decision": ["decision", "choice", "conclusion", "determination"],
    "users": ["users", "customers", "clients", "people"],
    "customers": ["customers", "buyers", "users", "clients"],
    "employees": ["employees", "workers", "staff", "team members"]
}


def normalize(text):
    return " ".join(text.lower().split())


def replace_words(text):
    result = text

    keys = list(SUBSTITUTIONS.keys())
    random.shuffle(keys)

    for word in keys[:random.randint(1, 3)]:

        if word.lower() in result.lower():

            replacement = random.choice(
                SUBSTITUTIONS[word]
            )

            result = result.replace(
                word,
                replacement
            )

            result = result.replace(
                word.capitalize(),
                replacement.capitalize()
            )

    return result


def generate_variations(text, labels, family_id, count=20):

    results = []

    results.append({
        "text": text,
        "labels": labels,
        "family_id": family_id
    })

    attempts = 0

    while len(results) < count and attempts < count * 30:

        attempts += 1

        candidate = text

        operations = random.sample(
            ["words", "prefix", "suffix"],
            k=random.randint(1, 3)
        )

        for operation in operations:

            if operation == "words":
                candidate = replace_words(candidate)

            elif operation == "prefix":

                prefix = random.choice(PREFIXES)

                if prefix:
                    candidate = (
                        prefix
                        + candidate[0].lower()
                        + candidate[1:]
                    )

            elif operation == "suffix":

                suffix = random.choice(SUFFIXES)

                if suffix:

                    base = candidate.rstrip(".!?")

                    if suffix.startswith("."):
                        candidate = base + suffix
                    else:
                        candidate = (
                            base + "." + suffix
                        )

        candidate = " ".join(
            candidate.split()
        ).strip()

        if candidate:

            results.append({
                "text": candidate,
                "labels": labels,
                "family_id": family_id
            })

    # Deduplicate within family.
    unique = {}

    for item in results:

        key = normalize(item["text"])

        if key not in unique:
            unique[key] = item

    return list(unique.values())


def label_count(data):

    counts = Counter()

    for item in data:

        for label in item["labels"]:
            counts[label] += 1

    return counts


def print_distribution(name, data):

    counts = label_count(data)

    multi = sum(
        len(x["labels"]) > 1
        for x in data
    )

    negatives = sum(
        len(x["labels"]) == 0
        for x in data
    )

    families = len({
        x["family_id"]
        for x in data
    })

    print(f"\n{name}: {len(data)} examples")
    print(f"  Families: {families}")

    for label in LABELS:

        print(
            f"  {label:28} {counts[label]}"
        )

    print(
        f"  {'MULTI_LABEL':28} {multi}"
    )

    print(
        f"  {'HARD_NEGATIVES':28} {negatives}"
    )


def main():

    random.seed(SEED)

    print("=" * 60)
    print("M3 FINAL FAMILY-ISOLATED DATASET")
    print("=" * 60)

    seeds = []

    with INPUT.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            if line.strip():
                seeds.append(
                    json.loads(line)
                )

    print(f"Loaded seeds: {len(seeds)}")

    # --------------------------------------------------
    # Identify label groups
    # --------------------------------------------------

    label_to_seeds = {
        label: []
        for label in LABELS
    }

    for i, item in enumerate(seeds):

        for label in item["labels"]:

            label_to_seeds[label].append(i)

    # --------------------------------------------------
    # First distribute seeds so every label appears
    # in train / validation / test.
    # --------------------------------------------------

    train_ids = set()
    val_ids = set()
    test_ids = set()

    # Randomized seed order.
    all_ids = list(range(len(seeds)))
    random.shuffle(all_ids)

    # Target number of seed families.
    train_target = 46
    val_target = 6
    test_target = 6

    # Select test families first.
    # Prefer families covering labels that are rare.
    assigned = set()

    label_order = sorted(
        LABELS,
        key=lambda x: len(label_to_seeds[x])
    )

    for label in label_order:

        candidates = [
            i
            for i in label_to_seeds[label]
            if i not in assigned
        ]

        if candidates:

            i = random.choice(candidates)

            test_ids.add(i)
            assigned.add(i)

    # Select validation families.
    for label in label_order:

        candidates = [
            i
            for i in label_to_seeds[label]
            if i not in assigned
        ]

        if candidates:

            i = random.choice(candidates)

            val_ids.add(i)
            assigned.add(i)

    # Fill remaining validation families.
    for i in all_ids:

        if len(val_ids) >= val_target:
            break

        if i not in assigned:

            val_ids.add(i)
            assigned.add(i)

    # Fill remaining test families.
    for i in all_ids:

        if len(test_ids) >= test_target:
            break

        if i not in assigned:

            test_ids.add(i)
            assigned.add(i)

    # Everything else goes to training.
    for i in all_ids:

        if i not in assigned:

            train_ids.add(i)

    # Safety check.
    print("\nSeed family allocation:")

    print(f"  Train families: {len(train_ids)}")
    print(f"  Val families:   {len(val_ids)}")
    print(f"  Test families:  {len(test_ids)}")

    # --------------------------------------------------
    # Generate examples independently inside each split
    # --------------------------------------------------

    train = []
    val = []
    test = []

    for i in sorted(train_ids):

        family = f"logician_seed_{i:03d}"

        train.extend(
            generate_variations(
                seeds[i]["text"],
                seeds[i]["labels"],
                family
            )
        )

    for i in sorted(val_ids):

        family = f"logician_seed_{i:03d}"

        val.extend(
            generate_variations(
                seeds[i]["text"],
                seeds[i]["labels"],
                family
            )
        )

    for i in sorted(test_ids):

        family = f"logician_seed_{i:03d}"

        test.extend(
            generate_variations(
                seeds[i]["text"],
                seeds[i]["labels"],
                family
            )
        )

    # --------------------------------------------------
    # Global exact deduplication
    # --------------------------------------------------

    def deduplicate(data):

        unique = {}

        for item in data:

            key = normalize(item["text"])

            if key not in unique:
                unique[key] = item

        return list(unique.values())

    train = deduplicate(train)
    val = deduplicate(val)
    test = deduplicate(test)

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True
    )

    def write(path, data):

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

    write(TRAIN_OUT, train)
    write(VAL_OUT, val)
    write(TEST_OUT, test)

    # --------------------------------------------------
    # Print distributions
    # --------------------------------------------------

    print_distribution(
        "TRAIN",
        train
    )

    print_distribution(
        "VALIDATION",
        val
    )

    print_distribution(
        "TEST",
        test
    )

    # --------------------------------------------------
    # Leakage verification
    # --------------------------------------------------

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

    train_families = {
        x["family_id"]
        for x in train
    }

    val_families = {
        x["family_id"]
        for x in val
    }

    test_families = {
        x["family_id"]
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
