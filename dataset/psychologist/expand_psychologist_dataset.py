import json
import random
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "psychologist"
    / "psychologist_seed.jsonl"
)

OUTPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "psychologist"
    / "psychologist_v2.jsonl"
)

SEED = 42

random.seed(SEED)


# ============================================================
# LABELS
# ============================================================

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
# VARIATION COMPONENTS
# ============================================================

SUBJECTS = [
    "I",
    "we",
    "they",
    "she",
    "he",
]

ACTIONS = [
    "finished the project",
    "received the result",
    "got the update",
    "completed the task",
    "heard the news",
    "joined the meeting",
    "received the offer",
    "completed the presentation",
]

POSITIVE_EVENTS = [
    "the promotion",
    "the good news",
    "the successful result",
    "the opportunity",
    "the final approval",
    "the achievement",
]

DECISIONS = [
    "you decide",
    "you choose",
    "whatever works for you",
    "do what you think is best",
    "make the decision yourself",
]

TASKS = [
    "handle it",
    "finish it",
    "take care of it",
    "fix it",
    "deal with it",
]

EMOTION_WORDS = [
    "happy",
    "excited",
    "thrilled",
    "grateful",
    "proud",
    "pleased",
]

HEDGING_WORDS = [
    "I guess",
    "I suppose",
    "maybe",
    "probably",
    "more or less",
    "kind of",
]


# ============================================================
# GENERATION HELPERS
# ============================================================

def add_example(
    examples,
    text,
    labels
):

    examples.append(
        {
            "text": text,
            "labels": labels
        }
    )


# ============================================================
# AFFECT GAP
# ============================================================

def generate_affect_gap():

    examples = []

    for event in POSITIVE_EVENTS:

        add_example(
            examples,
            f"I received {event}, but I do not really have much to say about it.",
            ["AFFECT_GAP"]
        )

        add_example(
            examples,
            f"I got {event}, although I do not feel much about it.",
            ["AFFECT_GAP"]
        )

        add_example(
            examples,
            f"Everyone was happy about {event}, but I did not really react.",
            ["AFFECT_GAP"]
        )

        add_example(
            examples,
            f"{event.capitalize()} happened, but I am keeping my reaction to myself.",
            ["AFFECT_GAP"]
        )

    return examples


# ============================================================
# FORCED POLITENESS
# ============================================================

def generate_forced_politeness():

    examples = []

    phrases = [
        "Sure, that is completely fine.",
        "Of course, no problem at all.",
        "Absolutely, whatever works for you.",
        "Sure, I would be more than happy to help.",
        "Of course, that sounds perfectly fine.",
        "No worries whatsoever.",
        "Absolutely, I am totally fine with that.",
        "Sure, I am happy to do it.",
    ]

    endings = [
        "",
        " Really.",
        " Of course.",
        " No problem.",
        " That is completely okay.",
        " Whatever you prefer.",
    ]

    for phrase in phrases:

        for ending in endings:

            add_example(
                examples,
                phrase + ending,
                ["FORCED_POLITENESS"]
            )

    return examples


# ============================================================
# EMOTIONAL INCONGRUENCE
# ============================================================

def generate_emotional_incongruence():

    examples = []

    for emotion in EMOTION_WORDS:

        add_example(
            examples,
            f"I am {emotion} about this, I guess.",
            ["EMOTIONAL_INCONGRUENCE"]
        )

        add_example(
            examples,
            f"I am very {emotion}, although I do not really feel that way.",
            ["EMOTIONAL_INCONGRUENCE"]
        )

        add_example(
            examples,
            f"This is great news, but honestly I feel nothing.",
            ["EMOTIONAL_INCONGRUENCE"]
        )

        add_example(
            examples,
            f"I should be {emotion} about this, but I am not.",
            ["EMOTIONAL_INCONGRUENCE"]
        )

    return examples


# ============================================================
# DISENGAGEMENT
# ============================================================

def generate_disengagement():

    examples = []

    for decision in DECISIONS:

        add_example(
            examples,
            f"{decision}. I do not really mind.",
            ["DISENGAGEMENT_SIGNAL"]
        )

        add_example(
            examples,
            f"{decision}. I have nothing else to add.",
            ["DISENGAGEMENT_SIGNAL"]
        )

        add_example(
            examples,
            f"{decision}. It is up to you.",
            ["DISENGAGEMENT_SIGNAL"]
        )

        add_example(
            examples,
            f"{decision}. I am not bothered either way.",
            ["DISENGAGEMENT_SIGNAL"]
        )

    return examples


# ============================================================
# RESENTMENT
# ============================================================

def generate_resentment():

    examples = []

    for task in TASKS:

        add_example(
            examples,
            f"Sure, I will {task} again. I usually end up doing it anyway.",
            ["RESENTMENT_SIGNAL"]
        )

        add_example(
            examples,
            f"No problem, I will {task} like always.",
            ["RESENTMENT_SIGNAL"]
        )

        add_example(
            examples,
            f"Of course, I can {task}. Someone has to do it.",
            ["RESENTMENT_SIGNAL"]
        )

        add_example(
            examples,
            f"I will {task}, since apparently nobody else can.",
            ["RESENTMENT_SIGNAL"]
        )

    return examples


# ============================================================
# EMOTIONAL AVOIDANCE
# ============================================================

def generate_emotional_avoidance():

    examples = []

    statements = [
        "I would rather not talk about how I feel.",
        "Let's not get into my feelings about this.",
        "I do not want to discuss the emotional side of this.",
        "I would prefer to keep my feelings out of this.",
        "There is no need to discuss how I feel.",
        "Let's focus on the practical part instead.",
        "I am not going to talk about my emotions right now.",
        "I would rather leave the emotional part alone.",
        "We can discuss the facts without discussing feelings.",
        "I do not want to get into that emotionally.",
    ]

    for statement in statements:

        add_example(
            examples,
            statement,
            ["EMOTIONAL_AVOIDANCE"]
        )

    return examples


# ============================================================
# NO AFFECT SIGNAL
# ============================================================

def generate_no_affect():

    examples = []

    neutral_templates = [
        "The meeting starts at ten tomorrow.",
        "The assignment is due on Friday.",
        "The package arrived this afternoon.",
        "The server was restarted after the update.",
        "I uploaded the document to the shared folder.",
        "The report contains five sections.",
        "The database was updated yesterday.",
        "The presentation begins at nine.",
        "The file was moved to the project folder.",
        "The application is running on port 8000.",
        "The class ends at four o'clock.",
        "The document has been submitted.",
        "The test will run for thirty minutes.",
        "The new version was released yesterday.",
        "The meeting room has been changed.",
    ]

    for statement in neutral_templates:

        add_example(
            examples,
            statement,
            ["NO_AFFECT_SIGNAL"]
        )

    return examples


# ============================================================
# MULTI-LABEL EXAMPLES
# ============================================================

def generate_multi_label():

    examples = []

    multi = [

        (
            "Sure, whatever you decide is fine. I do not really care anymore.",
            [
                "FORCED_POLITENESS",
                "DISENGAGEMENT_SIGNAL"
            ]
        ),

        (
            "Of course, I am happy to help again. I always end up doing everything anyway.",
            [
                "FORCED_POLITENESS",
                "RESENTMENT_SIGNAL"
            ]
        ),

        (
            "I am excited about the result, I guess, although honestly I feel nothing.",
            [
                "EMOTIONAL_INCONGRUENCE",
                "AFFECT_GAP"
            ]
        ),

        (
            "It is completely fine. I would rather not discuss how I actually feel.",
            [
                "FORCED_POLITENESS",
                "EMOTIONAL_AVOIDANCE"
            ]
        ),

        (
            "You decide. I have nothing else to say and I would rather not discuss it.",
            [
                "DISENGAGEMENT_SIGNAL",
                "EMOTIONAL_AVOIDANCE"
            ]
        ),

        (
            "Great, another task for me. No problem, I will handle it like always.",
            [
                "RESENTMENT_SIGNAL",
                "FORCED_POLITENESS"
            ]
        ),

        (
            "Sure, I guess this is great news, although I do not really feel anything.",
            [
                "FORCED_POLITENESS",
                "EMOTIONAL_INCONGRUENCE",
                "AFFECT_GAP"
            ]
        ),

        (
            "Whatever works for you. I am happy to help, as usual.",
            [
                "FORCED_POLITENESS",
                "DISENGAGEMENT_SIGNAL"
            ]
        ),
    ]

    for text, labels in multi:

        add_example(
            examples,
            text,
            labels
        )

    return examples


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load seeds
    # --------------------------------------------------------

    seed_examples = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            if line.strip():

                seed_examples.append(
                    json.loads(line)
                )

    print("=" * 70)
    print(
        "L.I.M.I.N.A.L. — "
        "PSYCHOLOGIST DATASET EXPANSION"
    )
    print("=" * 70)

    print(
        f"\nSeed examples: "
        f"{len(seed_examples)}"
    )

    # --------------------------------------------------------
    # Generate variations
    # --------------------------------------------------------

    generated = []

    generated.extend(
        generate_affect_gap()
    )

    generated.extend(
        generate_forced_politeness()
    )

    generated.extend(
        generate_emotional_incongruence()
    )

    generated.extend(
        generate_disengagement()
    )

    generated.extend(
        generate_resentment()
    )

    generated.extend(
        generate_emotional_avoidance()
    )

    generated.extend(
        generate_no_affect()
    )

    generated.extend(
        generate_multi_label()
    )

    print(
        f"Generated variations: "
        f"{len(generated)}"
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    all_examples = (
        seed_examples
        + generated
    )

    # --------------------------------------------------------
    # Remove exact duplicates
    # --------------------------------------------------------

    unique = {}

    for example in all_examples:

        key = (
            example["text"].strip().lower(),
            tuple(sorted(example["labels"]))
        )

        unique[key] = example

    final_examples = list(
        unique.values()
    )

    random.shuffle(
        final_examples
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for example in final_examples:

            f.write(
                json.dumps(
                    example,
                    ensure_ascii=False
                ) + "\n"
            )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    counts = {
        label: 0
        for label in LABELS
    }

    multi_label = 0

    for example in final_examples:

        if len(example["labels"]) > 1:

            multi_label += 1

        for label in example["labels"]:

            counts[label] += 1

    print(
        f"\nFinal unique examples: "
        f"{len(final_examples)}"
    )

    print(
        f"Multi-label examples: "
        f"{multi_label}"
    )

    print(
        "\nLabel distribution:"
    )

    for label in LABELS:

        print(
            f"  {label:30}"
            f"{counts[label]}"
        )

    print(
        f"\nSaved to:\n{OUTPUT_FILE}"
    )

    print(
        "\nExpansion complete."
    )


if __name__ == "__main__":

    main()