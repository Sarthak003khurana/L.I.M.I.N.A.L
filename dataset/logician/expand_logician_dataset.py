import json
import random
from pathlib import Path

INPUT = Path("dataset/logician/logician_seeds.jsonl")
OUTPUT = Path("dataset/logician/logician_expanded.jsonl")

random.seed(42)

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
    "employees": ["employees", "workers", "staff", "team members"],
}

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
    "The analysis concludes that ",
]

SUFFIXES = [
    "",
    ".",
    " This seems reasonable.",
    " That is why we should proceed.",
    " Therefore, the decision is obvious.",
    " For that reason, the team should agree.",
    " This is presented as sufficient evidence.",
]


def replace_words(text):
    result = text

    keys = list(SUBSTITUTIONS.keys())
    random.shuffle(keys)

    for word in keys[:random.randint(1, 3)]:
        if word.lower() in result.lower():
            replacement = random.choice(SUBSTITUTIONS[word])

            result = result.replace(word, replacement)
            result = result.replace(
                word.capitalize(),
                replacement.capitalize()
            )

    return result


def add_prefix(text):
    prefix = random.choice(PREFIXES)

    if not prefix:
        return text

    return prefix + text[0].lower() + text[1:]


def add_suffix(text):
    suffix = random.choice(SUFFIXES)

    if not suffix:
        return text

    base = text.rstrip(".!?")

    if suffix.startswith("."):
        return base + suffix

    return base + "." + suffix


def generate_variations(seed_text, labels, family_id, count):

    results = [{
        "text": seed_text,
        "labels": labels,
        "family_id": family_id
    }]

    attempts = 0

    while len(results) < count and attempts < count * 30:

        attempts += 1

        candidate = seed_text

        operations = random.sample(
            ["words", "prefix", "suffix"],
            k=random.randint(1, 3)
        )

        for operation in operations:

            if operation == "words":
                candidate = replace_words(candidate)

            elif operation == "prefix":
                candidate = add_prefix(candidate)

            elif operation == "suffix":
                candidate = add_suffix(candidate)

        candidate = " ".join(candidate.split()).strip()

        if candidate and candidate != seed_text:

            results.append({
                "text": candidate,
                "labels": labels,
                "family_id": family_id
            })

    return results


def main():

    print("=" * 60)
    print("M3 LOGICIAN DATASET REGENERATION")
    print("=" * 60)

    seeds = []

    with INPUT.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                seeds.append(json.loads(line))

    print(f"Loaded seeds: {len(seeds)}")

    all_examples = []

    for index, item in enumerate(seeds):

        family_id = f"logician_seed_{index:03d}"

        variations = generate_variations(
            item["text"],
            item["labels"],
            family_id,
            20
        )

        all_examples.extend(variations)

    # Exact deduplication.
    # Keep family information.
    unique = {}

    for item in all_examples:

        key = " ".join(
            item["text"].lower().split()
        )

        if key not in unique:
            unique[key] = item

    final_examples = list(unique.values())

    random.shuffle(final_examples)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:

        for item in final_examples:

            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False
                ) + "\n"
            )

    print(f"Generated examples: {len(all_examples)}")
    print(f"Unique examples:    {len(final_examples)}")

    print("\nLabel distribution:")

    labels = [
        "SKIPPED_PREMISE",
        "UNANSWERED_COUNTERARGUMENT",
        "UNSUPPORTED_CONCLUSION",
        "UNSTATED_ASSUMPTION",
        "CONTRADICTION",
        "FALSE_DILEMMA"
    ]

    for label in labels:

        count = sum(
            label in item["labels"]
            for item in final_examples
        )

        print(f"  {label:28} {count}")

    multi = sum(
        len(item["labels"]) > 1
        for item in final_examples
    )

    negatives = sum(
        len(item["labels"]) == 0
        for item in final_examples
    )

    families = len({
        item["family_id"]
        for item in final_examples
    })

    print(f"\nFamilies:              {families}")
    print(f"Multi-label examples:  {multi}")
    print(f"Hard-negative examples:{negatives}")

    print(f"\nSaved to: {OUTPUT}")

    print("=" * 60)


if __name__ == "__main__":
    main()
