import json
import sys
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from models.synthesizer.model import SynthesizerModel


# ============================================================
# CONFIGURATION
# ============================================================

TEST_FILE = (
    ROOT
    / "dataset"
    / "synthesizer"
    / "test.jsonl"
)

CHECKPOINT_FILE = (
    ROOT
    / "checkpoints"
    / "synthesizer"
    / "best_model.pt"
)

OUTPUT_FILE = (
    ROOT
    / "checkpoints"
    / "synthesizer"
    / "test_evaluation.json"
)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)


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
# DATASET
# ============================================================

class SynthesizerDataset(Dataset):

    def __init__(self, path):

        self.examples = []

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                if line.strip():

                    self.examples.append(
                        json.loads(line)
                    )

    def __len__(self):

        return len(self.examples)

    def __getitem__(self, index):

        item = self.examples[index]

        features = torch.tensor(
            item["features"],
            dtype=torch.float32
        )

        label = item["label_id"]

        return features, label


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("L.I.M.I.N.A.L. M5 BLIND TEST")
    print("=" * 70)

    print(f"\nDevice: {DEVICE}")

    if torch.cuda.is_available():

        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

    # --------------------------------------------------------
    # Load checkpoint
    # --------------------------------------------------------

    checkpoint = torch.load(
        CHECKPOINT_FILE,
        map_location=DEVICE
    )

    model = SynthesizerModel(
        input_dim=checkpoint["input_dim"],
        hidden_dim=checkpoint["hidden_dim"],
        num_classes=checkpoint["num_classes"],
        dropout=checkpoint["dropout"],
    ).to(DEVICE)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    print(
        f"\nCheckpoint epoch: "
        f"{checkpoint['epoch']}"
    )

    print(
        f"Best validation accuracy: "
        f"{checkpoint['best_val_accuracy']:.4f}"
    )

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    dataset = SynthesizerDataset(
        TEST_FILE
    )

    loader = DataLoader(
        dataset,
        batch_size=128,
        shuffle=False
    )

    print(
        f"Blind test examples: "
        f"{len(dataset)}"
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    all_predictions = []
    all_targets = []
    all_confidences = []

    with torch.no_grad():

        for features, labels in loader:

            features = features.to(DEVICE)

            output = model(features)

            logits = output[
                "subtext_logits"
            ]

            confidence = output[
                "confidence"
            ]

            probabilities = torch.softmax(
                logits,
                dim=1
            )

            predictions = torch.argmax(
                probabilities,
                dim=1
            )

            all_predictions.extend(
                predictions.cpu().tolist()
            )

            all_targets.extend(
                labels.tolist()
            )

            all_confidences.extend(
                confidence.squeeze(1)
                .cpu()
                .tolist()
            )

    # --------------------------------------------------------
    # Overall metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        all_targets,
        all_predictions
    )

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            all_targets,
            all_predictions,
            labels=list(range(len(LABELS))),
            zero_division=0
        )
    )

    macro_precision = precision.mean()
    macro_recall = recall.mean()
    macro_f1 = f1.mean()

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        all_targets,
        all_predictions,
        labels=list(range(len(LABELS)))
    )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("OVERALL RESULTS")
    print("=" * 70)

    print(
        f"\nAccuracy:          {accuracy:.4f}"
    )

    print(
        f"Macro Precision:   {macro_precision:.4f}"
    )

    print(
        f"Macro Recall:      {macro_recall:.4f}"
    )

    print(
        f"Macro F1:          {macro_f1:.4f}"
    )

    print("\n" + "=" * 70)
    print("PER-LABEL RESULTS")
    print("=" * 70)

    for i, label in enumerate(LABELS):

        print(
            f"\n{label}"
        )

        print(
            f"  Precision: {precision[i]:.4f}"
        )

        print(
            f"  Recall:    {recall[i]:.4f}"
        )

        print(
            f"  F1:        {f1[i]:.4f}"
        )

        print(
            f"  Support:   {support[i]}"
        )

    # --------------------------------------------------------
    # Confidence statistics
    # --------------------------------------------------------

    avg_confidence = (
        sum(all_confidences)
        / len(all_confidences)
    )

    print("\n" + "=" * 70)
    print("CONFIDENCE")
    print("=" * 70)

    print(
        f"\nAverage predicted confidence: "
        f"{avg_confidence:.4f}"
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CONFUSION MATRIX")
    print("=" * 70)

    print("\nRows = Actual")
    print("Columns = Predicted\n")

    print(
        " " * 30
        + " ".join(
            f"{i:>4}"
            for i in range(len(LABELS))
        )
    )

    for i, row in enumerate(cm):

        print(
            f"{i:>2} "
            f"{LABELS[i]:<27}"
            + " ".join(
                f"{value:>4}"
                for value in row
            )
        )

    # --------------------------------------------------------
    # Save evaluation
    # --------------------------------------------------------

    results = {

        "test_examples": len(dataset),

        "checkpoint_epoch":
            checkpoint["epoch"],

        "best_validation_accuracy":
            checkpoint["best_val_accuracy"],

        "accuracy": accuracy,

        "macro_precision":
            float(macro_precision),

        "macro_recall":
            float(macro_recall),

        "macro_f1":
            float(macro_f1),

        "average_predicted_confidence":
            float(avg_confidence),

        "labels": LABELS,

        "per_label": {

            LABELS[i]: {

                "precision":
                    float(precision[i]),

                "recall":
                    float(recall[i]),

                "f1":
                    float(f1[i]),

                "support":
                    int(support[i])
            }

            for i in range(len(LABELS))
        },

        "confusion_matrix":
            cm.tolist()
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2
        )

    print(
        f"\nEvaluation saved to:"
        f"\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":

    main()