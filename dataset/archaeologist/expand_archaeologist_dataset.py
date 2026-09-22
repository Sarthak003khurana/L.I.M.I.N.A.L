import json
import random
import re
from pathlib import Path

# ============================================================
# L.I.M.I.N.A.L.
# ARCHAEOLOGIST — DATASET EXPANSION
# ============================================================

SEED = 42
random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "archaeologist_train.jsonl"

OUTPUT_FILE = BASE_DIR / "archaeologist_expanded.jsonl"


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
# CONTROLLED VARIATIONS
# ============================================================

VARIATIONS = {

    "HEDGING": [
        "maybe",
        "perhaps",
        "possibly",
        "probably",
        "I suppose",
        "I guess",
        "it might be",
        "it seems",
        "it could be",
        "I am not entirely sure",
    ],

    "MISSING_ACTOR": [
        "someone",
        "people",
        "they",
        "everyone",
        "apparently someone",
        "it",
    ],

    "VAGUE_REFERENCE": [
        "that",
        "that issue",
        "that thing",
        "it",
        "the matter",
        "the situation",
        "what happened earlier",
    ],

    "MISSING_COMMITMENT": [
        "sometime",
        "eventually",
        "later",
        "at some point",
        "when possible",
        "when things settle down",
        "in the future",
    ],

}


# ============================================================
# DOMAINS
# ============================================================

DOMAINS = [
    "project",
    "assignment",
    "meeting",
    "report",
    "proposal",
    "deadline",
    "client",
    "deployment",
    "presentation",
    "application",
    "system",
    "budget",
    "schedule",
    "documentation",
    "task",
]


# ============================================================
# ACTORS
# ============================================================

ACTORS = [
    "the manager",
    "the team",
    "the developer",
    "the department",
    "the coordinator",
    "the administrator",
    "the project lead",
    "the finance team",
    "the engineering team",
    "the client",
    "Sarah",
    "James",
    "Rahul",
    "Priya",
    "the supervisor",
]


# ============================================================
# TIME EXPRESSIONS
# ============================================================

TIMES = [
    "today",
    "tomorrow",
    "yesterday",
    "this morning",
    "this afternoon",
    "next week",
    "by Friday",
    "before the meeting",
    "after the review",
]


# ============================================================
# READ SEED DATA
# ============================================================

def load_jsonl(path):

    data = []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            data.append(
                json.loads(line)
            )

    return data


seed_examples = load_jsonl(INPUT_FILE)


# ============================================================
# NORMALIZATION
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

def make_example(
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
# GENERATORS
# ============================================================

def generate_passive_examples():

    generated = []

    objects = [
        "The report",
        "The proposal",
        "The request",
        "The application",
        "The document",
        "The payment",
        "The configuration",
        "The schedule",
        "The presentation",
        "The assignment",
    ]

    verbs = [
        "was approved",
        "was submitted",
        "was reviewed",
        "was changed",
        "was completed",
        "was rejected",
        "was discussed",
        "was updated",
        "was modified",
        "was processed",
    ]

    for obj in objects:

        for verb in verbs:

            # Passive + missing actor
            generated.append(
                make_example(
                    f"{obj} {verb} yesterday.",
                    [
                        "PASSIVE_CONSTRUCTION",
                        "MISSING_ACTOR",
                    ],
                    "controlled_generation",
                    "easy",
                )
            )

            # Passive + explicit actor
            actor = random.choice(ACTORS)

            generated.append(
                make_example(
                    f"{obj} {verb} by {actor}.",
                    [
                        "PASSIVE_CONSTRUCTION",
                    ],
                    "hard_negative",
                    "medium",
                )
            )

    return generated


def generate_active_examples():

    generated = []

    objects = [
        "the report",
        "the proposal",
        "the request",
        "the application",
        "the document",
        "the payment",
        "the configuration",
        "the schedule",
    ]

    verbs = [
        "approved",
        "submitted",
        "reviewed",
        "changed",
        "completed",
        "rejected",
        "discussed",
        "updated",
    ]

    for actor in ACTORS:

        for obj in objects:

            verb = random.choice(verbs)

            generated.append(
                make_example(
                    f"{actor.capitalize()} {verb} {obj} yesterday.",
                    [
                        "NO_OMISSION",
                    ],
                    "hard_negative",
                    "medium",
                )
            )

    return generated


def generate_hedging_examples():

    generated = []

    subjects = [
        "We",
        "I",
        "The team",
        "This approach",
        "The proposal",
        "The project",
    ]

    actions = [
        "should review the plan",
        "could change the schedule",
        "might need another solution",
        "should discuss the issue",
        "could revisit the proposal",
        "might require more time",
        "should consider another option",
    ]

    for hedge in VARIATIONS["HEDGING"]:

        for action in actions:

            subject = random.choice(subjects)

            generated.append(
                make_example(
                    f"{subject} {hedge} {action}.",
                    [
                        "HEDGING",
                    ],
                    "controlled_generation",
                    "easy",
                )
            )

    return generated


def generate_vague_reference_examples():

    generated = []

    actions = [
        "should be handled",
        "needs attention",
        "should be discussed",
        "needs to be fixed",
        "can be addressed later",
        "still needs work",
        "should be reviewed",
    ]

    for reference in VARIATIONS["VAGUE_REFERENCE"]:

        for action in actions:

            generated.append(
                make_example(
                    f"We should {reference} {action}.",
                    [
                        "VAGUE_REFERENCE",
                    ],
                    "controlled_generation",
                    "easy",
                )
            )

    return generated


def generate_missing_commitment_examples():

    generated = []

    subjects = [
        "I",
        "We",
        "The team",
        "Someone",
    ]

    actions = [
        "will look into it",
        "will review the issue",
        "should discuss the matter",
        "can handle the problem",
        "will respond",
        "will address the concern",
        "should investigate this",
    ]

    for subject in subjects:

        for action in actions:

            time_expression = random.choice(
                VARIATIONS["MISSING_COMMITMENT"]
            )

            generated.append(
                make_example(
                    f"{subject} {action} {time_expression}.",
                    [
                        "MISSING_COMMITMENT",
                    ],
                    "controlled_generation",
                    "medium",
                )
            )

    return generated


def generate_actor_examples():

    generated = []

    actions = [
        "should handle the report",
        "will review the proposal",
        "changed the schedule",
        "approved the request",
        "will contact the client",
        "made the decision",
    ]

    vague_actors = [
        "Someone",
        "People",
        "They",
        "Everyone",
        "Apparently someone",
    ]

    for actor in vague_actors:

        for action in actions:

            generated.append(
                make_example(
                    f"{actor} {action}.",
                    [
                        "MISSING_ACTOR",
                    ],
                    "controlled_generation",
                    "medium",
                )
            )

    return generated


def generate_responsibility_examples():

    generated = []

    templates = [
        "I was only following instructions from everyone else.",
        "That was not really my decision.",
        "I only did what I was told.",
        "There was nothing I could do about the situation.",
        "The decision had already been made before I arrived.",
        "I was not responsible for that part.",
        "That was handled by someone else.",
        "I simply followed the process that was given to me.",
        "The team made the decision, not me.",
        "I was just doing what the manager requested.",
        "That issue was outside my responsibility.",
        "I had no control over what happened.",
    ]

    for text in templates:

        generated.append(
            make_example(
                text,
                [
                    "RESPONSIBILITY_AVOIDANCE",
                ],
                "controlled_generation",
                "medium",
            )
        )

    return generated


# ============================================================
# MULTI-LABEL GENERATORS
# ============================================================

def generate_combined_examples():

    generated = []

    for _ in range(500):

        hedge = random.choice(
            VARIATIONS["HEDGING"]
        )

        reference = random.choice(
            VARIATIONS["VAGUE_REFERENCE"]
        )

        time_expression = random.choice(
            VARIATIONS["MISSING_COMMITMENT"]
        )

        examples = [

            (
                f"{hedge}, we should handle "
                f"{reference} {time_expression}.",
                [
                    "HEDGING",
                    "VAGUE_REFERENCE",
                    "MISSING_COMMITMENT",
                ],
            ),

            (
                f"{hedge}, {reference} "
                f"was probably handled already.",
                [
                    "HEDGING",
                    "VAGUE_REFERENCE",
                    "PASSIVE_CONSTRUCTION",
                    "MISSING_ACTOR",
                ],
            ),

            (
                f"{reference} was changed "
                f"{time_expression}.",
                [
                    "VAGUE_REFERENCE",
                    "PASSIVE_CONSTRUCTION",
                    "MISSING_ACTOR",
                ],
            ),
        ]

        text, labels = random.choice(examples)

        generated.append(
            make_example(
                text,
                labels,
                "multi_label_generation",
                "hard",
            )
        )

    return generated


# ============================================================
# GENERATE DATA
# ============================================================

generated = []

generated.extend(
    generate_passive_examples()
)

generated.extend(
    generate_active_examples()
)

generated.extend(
    generate_hedging_examples()
)

generated.extend(
    generate_vague_reference_examples()
)

generated.extend(
    generate_missing_commitment_examples()
)

generated.extend(
    generate_actor_examples()
)

generated.extend(
    generate_responsibility_examples()
)

generated.extend(
    generate_combined_examples()
)


# ============================================================
# INCLUDE ORIGINAL SEEDS
# ============================================================

for example in seed_examples:

    generated.append(
        make_example(
            example["text"],
            example["labels"],
            "human_seed",
            "medium",
        )
    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

unique = {}

for example in generated:

    key = (
        example["text"].lower(),
        tuple(example["labels"])
    )

    if key not in unique:

        unique[key] = example


generated = list(
    unique.values()
)


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(generated)


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    for example in generated:

        file.write(
            json.dumps(
                example,
                ensure_ascii=False
            ) + "\n"
        )


# ============================================================
# STATISTICS
# ============================================================

label_counts = {
    label: 0
    for label in LABELS
}

for example in generated:

    for label in example["labels"]:

        label_counts[label] += 1


print("=" * 60)
print("L.I.M.I.N.A.L. ARCHAEOLOGIST DATASET EXPANSION")
print("=" * 60)

print()

print(
    f"Seed examples       : {len(seed_examples)}"
)

print(
    f"Expanded examples   : {len(generated)}"
)

print()

print("Label distribution:")
print("-" * 60)

for label in LABELS:

    print(
        f"{label:<28} : {label_counts[label]}"
    )

print()

print("Output:")
print(OUTPUT_FILE)

print()

print("Expansion complete.")