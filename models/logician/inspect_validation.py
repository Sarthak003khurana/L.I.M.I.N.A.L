import json
import re
import sys
from pathlib import Path

import torch


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from models.logician.model import LogicianTransformer


VAL_FILE = (
    PROJECT_ROOT
    / "dataset/logician/logician_v3/val.jsonl"
)

VOCAB_FILE = (
    PROJECT_ROOT
    / "models/logician/tokenizer/vocab.json"
)

CHECKPOINT = (
    PROJECT_ROOT
    / "checkpoints/logician/best_model.pt"
)

LABELS = [
    "SKIPPED_PREMISE",
    "UNANSWERED_COUNTERARGUMENT",
    "UNSUPPORTED_CONCLUSION",
    "UNSTATED_ASSUMPTION",
    "CONTRADICTION",
    "FALSE_DILEMMA"
]

PAD_ID = 0
UNK_ID = 1
BOS_ID = 2
EOS_ID = 3

MAX_SEQ_LEN = 128


def tokenize(text):

    return re.findall(
        r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?|[^\w\s]",
        text.lower()
    )


def encode(text, vocab):

    tokens = tokenize(text)

    ids = [
        vocab.get(token, UNK_ID)
        for token in tokens
    ]

    ids = ids[:MAX_SEQ_LEN - 2]

    ids = (
        [BOS_ID]
        + ids
        + [EOS_ID]
    )

    mask = [1] * len(ids)

    padding = (
        MAX_SEQ_LEN - len(ids)
    )

    ids += [PAD_ID] * padding
    mask += [0] * padding

    return (
        torch.tensor(
            [ids],
            dtype=torch.long
        ),
        torch.tensor(
            [mask],
            dtype=torch.long
        )
    )


def main():

    print("=" * 60)
    print("M3 VALIDATION INSPECTION")
    print("=" * 60)

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    with VOCAB_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        vocab = json.load(f)

    checkpoint = torch.load(
        CHECKPOINT,
        map_location=device
    )

    model = LogicianTransformer(
        vocab_size=len(vocab),
        num_labels=len(LABELS)
    ).to(device)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    print(
        f"Checkpoint epoch: "
        f"{checkpoint['epoch']}"
    )

    print(
        f"Validation F1 at checkpoint: "
        f"{checkpoint['best_val_f1']:.4f}"
    )

    print()

    with VAL_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        data = [
            json.loads(line)
            for line in f
            if line.strip()
        ]

    # Track correct / wrong predictions.
    correct = 0

    label_stats = {
        label: {
            "correct": 0,
            "wrong": 0
        }
        for label in LABELS
    }

    wrong_examples = []

    with torch.no_grad():

        for item in data:

            input_ids, mask = encode(
                item["text"],
                vocab
            )

            input_ids = input_ids.to(
                device
            )

            mask = mask.to(
                device
            )

            logits = model(
                input_ids,
                mask
            )

            probabilities = torch.sigmoid(
                logits
            )[0]

            prediction_ids = (
                probabilities >= 0.5
            ).nonzero(
                as_tuple=True
            )[0].tolist()

            predicted = [
                LABELS[i]
                for i in prediction_ids
            ]

            actual = item["labels"]

            predicted_set = set(predicted)
            actual_set = set(actual)

            if predicted_set == actual_set:

                correct += 1

            else:

                wrong_examples.append({
                    "text": item["text"],
                    "actual": actual,
                    "predicted": predicted,
                    "probabilities": {
                        LABELS[i]:
                        round(
                            probabilities[i].item(),
                            3
                        )
                        for i in range(
                            len(LABELS)
                        )
                    }
                })

            for label in LABELS:

                actual_has = (
                    label in actual_set
                )

                predicted_has = (
                    label in predicted_set
                )

                if actual_has == predicted_has:
                    label_stats[label]["correct"] += 1
                else:
                    label_stats[label]["wrong"] += 1

    print(
        f"Exact-set correct: "
        f"{correct}/{len(data)} "
        f"({correct / len(data) * 100:.1f}%)"
    )

    print("\nPer-label agreement:")

    for label in LABELS:

        stats = label_stats[label]

        total = (
            stats["correct"]
            + stats["wrong"]
        )

        accuracy = (
            stats["correct"]
            / total
            if total
            else 0
        )

        print(
            f"  {label:28} "
            f"{accuracy:.3f}"
        )

    print("\nFirst 20 incorrect validation examples:")
    print("-" * 60)

    for i, item in enumerate(
        wrong_examples[:20],
        start=1
    ):

        print(f"\n{i}. {item['text']}")
        print(
            f"   Actual:    "
            f"{item['actual']}"
        )
        print(
            f"   Predicted: "
            f"{item['predicted']}"
        )

        print(
            f"   Scores:    "
            f"{item['probabilities']}"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()
