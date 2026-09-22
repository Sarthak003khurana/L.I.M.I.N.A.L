import json
import sys
from pathlib import Path
from collections import Counter

import torch


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


TEST_FILE = (
    ROOT
    / "dataset"
    / "synthesizer"
    / "test.jsonl"
)

CHECKPOINT = (
    ROOT
    / "checkpoints"
    / "synthesizer"
    / "best_model.pt"
)


# ============================================================
# LABELS
# ============================================================

LABELS = [
    "NO_SIGNIFICANT_OMISSION",
    "UNSTATED_PREFERENCE",
    "AVOIDING_COMMITMENT",
    "DISTANCING_FROM_RESPONSIBILITY",
    "EMOTIONAL_DISENGAGEMENT",
    "WITHHELD_CONTEXT",
    "UNSUPPORTED_REASONING",
    "AMBIGUOUS_INTENT",
]


# ============================================================
# IMPORT MODEL
# ============================================================

from models.synthesizer.model import SynthesizerModel


# ============================================================
# LOAD DATA
# ============================================================

def load_jsonl(path):

    examples = []

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if line.strip():

                examples.append(
                    json.loads(line)
                )

    return examples


# ============================================================
# LOAD CHECKPOINT
# ============================================================

def load_model():

    checkpoint = torch.load(
        CHECKPOINT,
        map_location="cpu",
        weights_only=False,
    )

    metadata = checkpoint.get(
        "metadata",
        {}
    )

    input_dim = metadata.get(
        "input_dim",
        25,
    )

    hidden_dim = metadata.get(
        "hidden_dim",
        96,
    )

    num_classes = metadata.get(
        "num_classes",
        8,
    )

    dropout = metadata.get(
        "dropout",
        0.20,
    )

    model = SynthesizerModel(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        num_classes=num_classes,
        dropout=dropout,
    )

    state_dict = checkpoint.get(
        "model_state_dict",
        checkpoint.get(
            "state_dict"
        ),
    )

    model.load_state_dict(
        state_dict
    )

    model.eval()

    return model


# ============================================================
# PREDICT
# ============================================================

def predict(
    model,
    features,
    text,
):

    x = torch.tensor(
        [features],
        dtype=torch.float32,
    )

    with torch.no_grad():

        from models.synthesizer.model import text_to_token_ids

        token_ids = [text_to_token_ids(text)]
        output = model(x, token_ids)

        if isinstance(
            output,
            dict,
        ):

            logits = output[
                "subtext_logits"
            ]

        else:

            logits = output

        probabilities = torch.softmax(
            logits,
            dim=1,
        )[0]

        prediction = int(
            torch.argmax(
                probabilities
            ).item()
        )

        confidence = float(
            probabilities[
                prediction
            ].item()
        )

    return (
        prediction,
        confidence,
        probabilities.tolist(),
    )


# ============================================================
# CONFUSION MATRIX
# ============================================================

def print_confusion_matrix(
    actuals,
    predictions,
):

    matrix = [
        [0 for _ in LABELS]
        for _ in LABELS
    ]

    for actual, predicted in zip(
        actuals,
        predictions,
    ):

        matrix[
            actual
        ][
            predicted
        ] += 1

    print(
        "\n"
        + "=" * 90
    )

    print(
        "BLIND TEST CONFUSION MATRIX"
    )

    print(
        "=" * 90
    )

    print(
        "Rows = actual"
    )

    print(
        "Columns = predicted"
    )

    print()

    print(
        " " * 34
        + " ".join(
            f"{i:>4}"
            for i in range(
                len(LABELS)
            )
        )
    )

    for i, row in enumerate(
        matrix
    ):

        print(
            f"{i:>2} "
            f"{LABELS[i]:<32}"
            + " ".join(
                f"{value:>4}"
                for value in row
            )
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 90
    )

    print(
        "L.I.M.I.N.A.L. M5 BLIND TEST DIAGNOSTIC"
    )

    print(
        "=" * 90
    )

    print(
        f"\nTest dataset:"
    )

    print(
        TEST_FILE
    )

    print(
        f"\nCheckpoint:"
    )

    print(
        CHECKPOINT
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    examples = load_jsonl(
        TEST_FILE
    )

    print(
        f"\nLoaded test examples: "
        f"{len(examples)}"
    )

    model = load_model()

    print(
        "✓ M5 checkpoint loaded."
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    actuals = []
    predictions = []

    correct = 0

    class_correct = Counter()
    class_total = Counter()

    errors = []

    for index, example in enumerate(
        examples
    ):

        actual = int(
            example["label_id"]
        )

        predicted, confidence, probs = (
            predict(
                model,
                example["features"],
                example["text"],
            )
        )

        actuals.append(
            actual
        )

        predictions.append(
            predicted
        )

        class_total[
            actual
        ] += 1

        if actual == predicted:

            correct += 1

            class_correct[
                actual
            ] += 1

        else:

            errors.append(
                {
                    "index":
                        index,

                    "text":
                        example["text"],

                    "actual":
                        LABELS[actual],

                    "predicted":
                        LABELS[predicted],

                    "confidence":
                        confidence,

                    "probabilities":
                        probs,

                    "features":
                        example["features"],
                }
            )

    # --------------------------------------------------------
    # Overall accuracy
    # --------------------------------------------------------

    accuracy = (
        correct
        / len(examples)
    )

    print(
        "\n"
        + "=" * 90
    )

    print(
        "OVERALL RESULT"
    )

    print(
        "=" * 90
    )

    print(
        f"Correct: "
        f"{correct}/{len(examples)}"
    )

    print(
        f"Accuracy: "
        f"{accuracy:.4f}"
    )

    # --------------------------------------------------------
    # Per-class accuracy
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 90
    )

    print(
        "PER-CLASS RESULTS"
    )

    print(
        "=" * 90
    )

    for class_id, label in enumerate(
        LABELS
    ):

        total = class_total[
            class_id
        ]

        correct_class = class_correct[
            class_id
        ]

        class_accuracy = (
            correct_class
            / total
            if total
            else 0.0
        )

        print(
            f"{label:<35}"
            f"{correct_class:>3}/"
            f"{total:<3}"
            f"  Accuracy: "
            f"{class_accuracy:.4f}"
        )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    print_confusion_matrix(
        actuals,
        predictions,
    )

    # --------------------------------------------------------
    # Error analysis
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 90
    )

    print(
        f"ERROR ANALYSIS — {len(errors)} errors"
    )

    print(
        "=" * 90
    )

    for i, error in enumerate(
        errors,
        start=1,
    ):

        print(
            f"\n[{i}]"
        )

        print(
            f"Text       : "
            f"{error['text']}"
        )

        print(
            f"Actual     : "
            f"{error['actual']}"
        )

        print(
            f"Predicted  : "
            f"{error['predicted']}"
        )

        print(
            f"Confidence : "
            f"{error['confidence']:.4f}"
        )

        # Top 3 probabilities

        ranked = sorted(
            enumerate(
                error["probabilities"]
            ),
            key=lambda x: x[1],
            reverse=True,
        )[:3]

        print(
            "Top 3     :"
        )

        for class_id, probability in ranked:

            print(
                f"  {LABELS[class_id]:<35}"
                f"{probability:.4f}"
            )

    # --------------------------------------------------------
    # Confusion pairs
    # --------------------------------------------------------

    confusion_pairs = Counter()

    for actual, predicted in zip(
        actuals,
        predictions,
    ):

        if actual != predicted:

            confusion_pairs[
                (
                    LABELS[actual],
                    LABELS[predicted],
                )
            ] += 1

    print(
        "\n"
        + "=" * 90
    )

    print(
        "MOST COMMON CONFUSIONS"
    )

    print(
        "=" * 90
    )

    for (
        (actual, predicted),
        count,
    ) in confusion_pairs.most_common():

        print(
            f"{actual:<35}"
            f" -> "
            f"{predicted:<35}"
            f"{count}"
        )

    # --------------------------------------------------------
    # Important warning
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 90
    )

    print(
        "DIAGNOSTIC COMPLETE"
    )

    print(
        "=" * 90
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "The blind test was used ONLY for evaluation."
    )

    print(
        "Do not modify/retrain the model based on individual"
    )

    print(
        "test examples until we decide on the next dataset step."
    )


if __name__ == "__main__":

    main()