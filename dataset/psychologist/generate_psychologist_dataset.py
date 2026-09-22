import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "dataset" / "psychologist"
OUTPUT_FILE = OUTPUT_DIR / "psychologist_seed.jsonl"

SEED = 42

random.seed(SEED)


LABELS = [
    "NO_AFFECT_SIGNAL",
    "AFFECT_GAP",
    "FORCED_POLITENESS",
    "EMOTIONAL_INCONGRUENCE",
    "DISENGAGEMENT_SIGNAL",
    "RESENTMENT_SIGNAL",
    "EMOTIONAL_AVOIDANCE",
]


examples = [

    {
        "text": "The meeting starts at ten tomorrow.",
        "labels": ["NO_AFFECT_SIGNAL"]
    },
    {
        "text": "Please submit the assignment before Friday.",
        "labels": ["NO_AFFECT_SIGNAL"]
    },
    {
        "text": "The package arrived this afternoon.",
        "labels": ["NO_AFFECT_SIGNAL"]
    },
    {
        "text": "The server was restarted after the update.",
        "labels": ["NO_AFFECT_SIGNAL"]
    },
    {
        "text": "I uploaded the document to the shared folder.",
        "labels": ["NO_AFFECT_SIGNAL"]
    },

    {
        "text": "I got the promotion, but there is not much to say about it.",
        "labels": ["AFFECT_GAP"]
    },
    {
        "text": "Everyone congratulated me, although I do not really feel anything.",
        "labels": ["AFFECT_GAP"]
    },
    {
        "text": "The result was excellent, but I have nothing else to add.",
        "labels": ["AFFECT_GAP"]
    },
    {
        "text": "We finally finished the project, and that is all I will say about it.",
        "labels": ["AFFECT_GAP"]
    },
    {
        "text": "I received the good news yesterday, but I am keeping my reaction to myself.",
        "labels": ["AFFECT_GAP"]
    },

    {
        "text": "Sure, that is completely fine, no worries at all.",
        "labels": ["FORCED_POLITENESS"]
    },
    {
        "text": "Of course, I would absolutely love to do that.",
        "labels": ["FORCED_POLITENESS"]
    },
    {
        "text": "No problem whatsoever, whatever works for you is perfect.",
        "labels": ["FORCED_POLITENESS"]
    },
    {
        "text": "I am totally happy with whatever you decide.",
        "labels": ["FORCED_POLITENESS"]
    },
    {
        "text": "Absolutely, I am more than happy to help with this.",
        "labels": ["FORCED_POLITENESS"]
    },

    {
        "text": "I am thrilled about the opportunity, I guess.",
        "labels": ["EMOTIONAL_INCONGRUENCE"]
    },
    {
        "text": "This is fantastic news, although I do not really care.",
        "labels": ["EMOTIONAL_INCONGRUENCE"]
    },
    {
        "text": "I am very excited about it, but honestly I feel nothing.",
        "labels": ["EMOTIONAL_INCONGRUENCE"]
    },
    {
        "text": "Everything is wonderful, and I suppose that is good.",
        "labels": ["EMOTIONAL_INCONGRUENCE"]
    },
    {
        "text": "I am happy for everyone, although I am not particularly enthusiastic.",
        "labels": ["EMOTIONAL_INCONGRUENCE"]
    },

    {
        "text": "Whatever you want is fine with me.",
        "labels": ["DISENGAGEMENT_SIGNAL"]
    },
    {
        "text": "You can decide. I really do not mind.",
        "labels": ["DISENGAGEMENT_SIGNAL"]
    },
    {
        "text": "I do not have much to say about this anymore.",
        "labels": ["DISENGAGEMENT_SIGNAL"]
    },
    {
        "text": "Just do whatever works. I am not bothered.",
        "labels": ["DISENGAGEMENT_SIGNAL"]
    },
    {
        "text": "It is up to you. I have nothing else to contribute.",
        "labels": ["DISENGAGEMENT_SIGNAL"]
    },

    {
        "text": "Sure, I will handle it again since apparently nobody else can.",
        "labels": ["RESENTMENT_SIGNAL"]
    },
    {
        "text": "No problem, I am used to being the one who fixes everything.",
        "labels": ["RESENTMENT_SIGNAL"]
    },
    {
        "text": "It is fine, someone has to clean up the mess eventually.",
        "labels": ["RESENTMENT_SIGNAL"]
    },
    {
        "text": "Of course I can do it. I usually end up doing it anyway.",
        "labels": ["RESENTMENT_SIGNAL"]
    },
    {
        "text": "Do not worry, I will take care of it like always.",
        "labels": ["RESENTMENT_SIGNAL"]
    },

    {
        "text": "I would rather not talk about how I feel right now.",
        "labels": ["EMOTIONAL_AVOIDANCE"]
    },
    {
        "text": "There is no point discussing my feelings about this.",
        "labels": ["EMOTIONAL_AVOIDANCE"]
    },
    {
        "text": "I am not going to get into the emotional side of this.",
        "labels": ["EMOTIONAL_AVOIDANCE"]
    },
    {
        "text": "Let's just focus on what needs to be done.",
        "labels": ["EMOTIONAL_AVOIDANCE"]
    },
    {
        "text": "I would prefer to keep my feelings out of this conversation.",
        "labels": ["EMOTIONAL_AVOIDANCE"]
    },

    {
        "text": "Sure, whatever you decide is fine. I do not really care anymore.",
        "labels": [
            "FORCED_POLITENESS",
            "DISENGAGEMENT_SIGNAL"
        ]
    },
    {
        "text": "Of course I am happy to help again. I always end up doing everything anyway.",
        "labels": [
            "FORCED_POLITENESS",
            "RESENTMENT_SIGNAL"
        ]
    },
    {
        "text": "I am excited about this, I guess, although honestly I feel nothing.",
        "labels": [
            "EMOTIONAL_INCONGRUENCE",
            "AFFECT_GAP"
        ]
    },
    {
        "text": "It is completely fine. I would rather not discuss how I actually feel.",
        "labels": [
            "FORCED_POLITENESS",
            "EMOTIONAL_AVOIDANCE"
        ]
    },
    {
        "text": "You decide. I have nothing else to say and I would rather not discuss it.",
        "labels": [
            "DISENGAGEMENT_SIGNAL",
            "EMOTIONAL_AVOIDANCE"
        ]
    },
    {
        "text": "Great, another task for me. No problem, I will handle it like always.",
        "labels": [
            "RESENTMENT_SIGNAL",
            "FORCED_POLITENESS"
        ]
    },
]


def validate_examples(data):

    valid_labels = set(LABELS)

    for index, item in enumerate(data):

        if "text" not in item:
            raise ValueError(
                f"Example {index} is missing 'text'."
            )

        if "labels" not in item:
            raise ValueError(
                f"Example {index} is missing 'labels'."
            )

        if not isinstance(item["labels"], list):
            raise ValueError(
                f"Example {index} labels must be a list."
            )

        for label in item["labels"]:

            if label not in valid_labels:

                raise ValueError(
                    f"Unknown label '{label}' "
                    f"in example {index}."
                )


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    validate_examples(examples)

    random.shuffle(examples)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for item in examples:

            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False
                ) + "\n"
            )

    counts = {
        label: 0
        for label in LABELS
    }

    multi_label_count = 0

    for item in examples:

        if len(item["labels"]) > 1:
            multi_label_count += 1

        for label in item["labels"]:
            counts[label] += 1

    print("=" * 65)
    print(
        "L.I.M.I.N.A.L. — "
        "PSYCHOLOGIST SEED DATASET"
    )
    print("=" * 65)

    print(
        f"\nTotal examples: {len(examples)}"
    )

    print(
        f"Multi-label examples: "
        f"{multi_label_count}"
    )

    print("\nLabel distribution:")

    for label in LABELS:

        print(
            f"  {label:28} {counts[label]}"
        )

    print(
        f"\nSaved to:\n{OUTPUT_FILE}"
    )

    print(
        "\nDataset generation complete."
    )


if __name__ == "__main__":
    main()