import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.psychologist.model import PsychologistModel
from models.psychologist.train import (
    PsychologistDataset,
    load_vocab,
    LABELS,
)


DATASET_DIR = PROJECT_ROOT / "dataset" / "psychologist"

TEST_FILE = DATASET_DIR / "psychologist_v3_test.jsonl"

MODEL_DIR = PROJECT_ROOT / "models" / "psychologist"

TOKENIZER_FILE = MODEL_DIR / "tokenizer" / "vocab.json"

CHECKPOINT_FILE = (
    PROJECT_ROOT
    / "checkpoints"
    / "psychologist"
    / "best_model.pt"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "checkpoints"
    / "psychologist"
    / "test_evaluation.json"
)


def calculate_metrics(logits, targets, threshold=0.5):

    probabilities = torch.sigmoid(logits)

    predictions = (
        probabilities >= threshold
    ).int()

    targets = targets.int()

    true_positive = (
        (predictions == 1)
        & (targets == 1)
    ).sum(dim=0).float()

    false_positive = (
        (predictions == 1)
        & (targets == 0)
    ).sum(dim=0).float()

    false_negative = (
        (predictions == 0)
        & (targets == 1)
    ).sum(dim=0).float()

    true_negative = (
        (predictions == 0)
        & (targets == 0)
    ).sum(dim=0).float()

    precision = (
        true_positive
        / (
            true_positive
            + false_positive
            + 1e-8
        )
    )

    recall = (
        true_positive
        / (
            true_positive
            + false_negative
            + 1e-8
        )
    )

    f1 = (
        2
        * precision
        * recall
        / (
            precision
            + recall
            + 1e-8
        )
    )

    macro_precision = precision.mean().item()

    macro_recall = recall.mean().item()

    macro_f1 = f1.mean().item()

    total_tp = true_positive.sum()

    total_fp = false_positive.sum()

    total_fn = false_negative.sum()

    micro_precision = (
        total_tp
        / (
            total_tp
            + total_fp
            + 1e-8
        )
    ).item()

    micro_recall = (
        total_tp
        / (
            total_tp
            + total_fn
            + 1e-8
        )
    ).item()

    micro_f1 = (
        2
        * micro_precision
        * micro_recall
        / (
            micro_precision
            + micro_recall
            + 1e-8
        )
    )

    exact_match = (
        predictions == targets
    ).all(dim=1).float().mean().item()

    return {
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": micro_f1,
        "exact_match": exact_match,
        "per_label": {
            label: {
                "precision": precision[i].item(),
                "recall": recall[i].item(),
                "f1": f1[i].item(),
                "tp": int(true_positive[i].item()),
                "fp": int(false_positive[i].item()),
                "fn": int(false_negative[i].item()),
                "tn": int(true_negative[i].item()),
            }
            for i, label in enumerate(LABELS)
        },
    }


def main():

    print("=" * 70)
    print("L.I.M.I.N.A.L. — M2 PSYCHOLOGIST BLIND TEST")
    print("=" * 70)

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"\nDevice: {device}")

    if torch.cuda.is_available():
        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

    # --------------------------------------------------------
    # Load tokenizer
    # --------------------------------------------------------

    vocab = load_vocab()

    print(
        f"\nVocabulary size: "
        f"{len(vocab)}"
    )

    # --------------------------------------------------------
    # Load blind test dataset
    # --------------------------------------------------------

    test_dataset = PsychologistDataset(
        TEST_FILE,
        vocab,
    )

    print(
        f"Blind test examples: "
        f"{len(test_dataset)}"
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=32,
        shuffle=False,
        num_workers=0,
    )

    # --------------------------------------------------------
    # Load checkpoint
    # --------------------------------------------------------

    checkpoint = torch.load(
        CHECKPOINT_FILE,
        map_location=device,
    )

    model = PsychologistModel(
        vocab_size=checkpoint["vocab_size"],
        num_labels=checkpoint["num_labels"],
        embedding_dimension=checkpoint[
            "embedding_dimension"
        ],
        num_attention_heads=checkpoint[
            "num_attention_heads"
        ],
        num_transformer_layers=checkpoint[
            "num_transformer_layers"
        ],
        feed_forward_dimension=checkpoint[
            "feed_forward_dimension"
        ],
        max_sequence_length=checkpoint[
            "max_sequence_length"
        ],
        dropout=checkpoint["dropout"],
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
        f"Best validation F1: "
        f"{checkpoint['best_validation_f1']:.4f}"
    )

    # --------------------------------------------------------
    # Blind inference
    # --------------------------------------------------------

    all_logits = []

    all_targets = []

    with torch.no_grad():

        for input_ids, targets in test_loader:

            input_ids = input_ids.to(device)

            with torch.amp.autocast(
                "cuda",
                enabled=torch.cuda.is_available(),
            ):

                logits = model(
                    input_ids
                )

            all_logits.append(
                logits.cpu()
            )

            all_targets.append(
                targets
            )

    logits = torch.cat(
        all_logits
    )

    targets = torch.cat(
        all_targets
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    results = calculate_metrics(
        logits,
        targets,
    )

    print("\n" + "=" * 70)
    print("BLIND TEST RESULTS")
    print("=" * 70)

    print(
        f"\nMacro Precision : "
        f"{results['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall    : "
        f"{results['macro_recall']:.4f}"
    )

    print(
        f"Macro F1        : "
        f"{results['macro_f1']:.4f}"
    )

    print(
        f"\nMicro Precision : "
        f"{results['micro_precision']:.4f}"
    )

    print(
        f"Micro Recall    : "
        f"{results['micro_recall']:.4f}"
    )

    print(
        f"Micro F1        : "
        f"{results['micro_f1']:.4f}"
    )

    print(
        f"\nExact Match     : "
        f"{results['exact_match']:.4f}"
    )

    print("\nPer-label results:")

    for label, metrics in results[
        "per_label"
    ].items():

        print(
            f"\n{label}"
        )

        print(
            f"  Precision: "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"  Recall   : "
            f"{metrics['recall']:.4f}"
        )

        print(
            f"  F1       : "
            f"{metrics['f1']:.4f}"
        )

        print(
            f"  TP={metrics['tp']} "
            f"FP={metrics['fp']} "
            f"FN={metrics['fn']} "
            f"TN={metrics['tn']}"
        )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results["model"] = "M2 Psychologist"

    results["test_examples"] = len(
        test_dataset
    )

    results["checkpoint_epoch"] = checkpoint[
        "epoch"
    ]

    results["best_validation_f1"] = checkpoint[
        "best_validation_f1"
    ]

    results["threshold"] = 0.5

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
        )

    print(
        f"\nResults saved to:"
    )

    print(OUTPUT_FILE)

    print("\n" + "=" * 70)
    print("M2 BLIND TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
