import json
import sys
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from models.logician.model import LogicianTransformer

# ============================================================
# CONFIG
# ============================================================

TEST_FILE = ROOT / "dataset" / "logician" / "logician_v3" / "test.jsonl"
VOCAB_FILE = ROOT / "models" / "logician" / "tokenizer" / "vocab.json"
CHECKPOINT_FILE = ROOT / "checkpoints" / "logician" / "best_model.pt"
OUTPUT_FILE = ROOT / "checkpoints" / "logician" / "test_evaluation.json"

LABELS = [
    "SKIPPED_PREMISE",
    "UNANSWERED_COUNTERARGUMENT",
    "UNSUPPORTED_CONCLUSION",
    "UNSTATED_ASSUMPTION",
    "CONTRADICTION",
    "FALSE_DILEMMA",
]

MAX_SEQ_LEN = 128
BATCH_SIZE = 32
THRESHOLD = 0.5


# ============================================================
# TOKENIZER
# ============================================================

with open(VOCAB_FILE, "r", encoding="utf-8") as f:
    vocab = json.load(f)


PAD_ID = vocab["<PAD>"]
UNK_ID = vocab["<UNK>"]
BOS_ID = vocab["<BOS>"]
EOS_ID = vocab["<EOS>"]


def tokenize(text):
    words = text.lower().strip().split()

    ids = [BOS_ID]

    for word in words:
        ids.append(vocab.get(word, UNK_ID))

    ids.append(EOS_ID)

    ids = ids[:MAX_SEQ_LEN]

    attention_mask = [1] * len(ids)

    while len(ids) < MAX_SEQ_LEN:
        ids.append(PAD_ID)
        attention_mask.append(0)

    return ids, attention_mask


# ============================================================
# DATASET
# ============================================================

class LogicianTestDataset(Dataset):

    def __init__(self, path):
        self.examples = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                item = json.loads(line)

                labels = item.get("labels", [])

                target = [
                    1.0 if label in labels else 0.0
                    for label in LABELS
                ]

                input_ids, attention_mask = tokenize(item["text"])

                self.examples.append({
                    "text": item["text"],
                    "labels": labels,
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                    "target": target,
                })

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, index):
        item = self.examples[index]

        return {
            "text": item["text"],
            "labels": item["labels"],
            "input_ids": torch.tensor(
                item["input_ids"],
                dtype=torch.long
            ),
            "attention_mask": torch.tensor(
                item["attention_mask"],
                dtype=torch.long
            ),
            "target": torch.tensor(
                item["target"],
                dtype=torch.float32
            ),
        }


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(y_true, y_pred):

    results = {}

    tp_total = 0
    fp_total = 0
    fn_total = 0

    f1_values = []
    precision_values = []
    recall_values = []

    for i, label in enumerate(LABELS):

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        for true_row, pred_row in zip(y_true, y_pred):

            true_value = true_row[i]
            pred_value = pred_row[i]

            if true_value == 1 and pred_value == 1:
                tp += 1
            elif true_value == 0 and pred_value == 1:
                fp += 1
            elif true_value == 1 and pred_value == 0:
                fn += 1
            else:
                tn += 1

        precision = (
            tp / (tp + fp)
            if (tp + fp) > 0
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn) > 0
            else 0.0
        )

        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        results[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
        }

        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)

        tp_total += tp
        fp_total += fp
        fn_total += fn

    macro_precision = sum(precision_values) / len(LABELS)
    macro_recall = sum(recall_values) / len(LABELS)
    macro_f1 = sum(f1_values) / len(LABELS)

    micro_precision = (
        tp_total / (tp_total + fp_total)
        if tp_total + fp_total > 0
        else 0.0
    )

    micro_recall = (
        tp_total / (tp_total + fn_total)
        if tp_total + fn_total > 0
        else 0.0
    )

    micro_f1 = (
        2 * micro_precision * micro_recall
        / (micro_precision + micro_recall)
        if micro_precision + micro_recall > 0
        else 0.0
    )

    return {
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": micro_f1,
        "per_label": results,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("M3 LOGICIAN BLIND TEST EVALUATION")
    print("=" * 60)

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Device: {device}")

    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    dataset = LogicianTestDataset(TEST_FILE)

    print(f"Test examples: {len(dataset)}")
    print(f"Vocabulary size: {len(vocab)}")

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = LogicianTransformer(
        vocab_size=len(vocab),
        num_labels=len(LABELS),
        embedding_dim=192,
        num_heads=6,
        num_layers=3,
        feedforward_dim=768,
        max_seq_len=MAX_SEQ_LEN,
        dropout=0.30,
    )

    checkpoint = torch.load(
        CHECKPOINT_FILE,
        map_location=device,
        weights_only=False,
    )

    if "model_state_dict" in checkpoint:
        model.load_state_dict(
            checkpoint["model_state_dict"]
        )
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()

    checkpoint_epoch = checkpoint.get("epoch", "unknown")
    validation_f1 = checkpoint.get(
        "val_f1",
        checkpoint.get("best_val_f1", None)
    )

    print(f"Checkpoint epoch: {checkpoint_epoch}")

    if validation_f1 is not None:
        print(
            f"Validation F1 at checkpoint: "
            f"{validation_f1:.4f}"
        )

    # --------------------------------------------------------
    # Inference
    # --------------------------------------------------------

    all_true = []
    all_pred = []
    all_probs = []
    incorrect = []

    with torch.no_grad():

        for batch in loader:

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            logits = model(
                input_ids,
                attention_mask
            )

            probabilities = torch.sigmoid(logits)

            predictions = (
                probabilities >= THRESHOLD
            ).int()

            true_labels = batch["target"].int()

            for i in range(len(predictions)):

                true_row = true_labels[i].cpu().tolist()
                pred_row = predictions[i].cpu().tolist()
                prob_row = probabilities[i].cpu().tolist()

                all_true.append(true_row)
                all_pred.append(pred_row)
                all_probs.append(prob_row)

                if true_row != pred_row:

                    actual = [
                        LABELS[j]
                        for j, value in enumerate(true_row)
                        if value == 1
                    ]

                    predicted = [
                        LABELS[j]
                        for j, value in enumerate(pred_row)
                        if value == 1
                    ]

                    scores = {
                        LABELS[j]: round(
                            prob_row[j], 3
                        )
                        for j in range(len(LABELS))
                    }

                    incorrect.append({
                        "text": batch["text"][i],
                        "actual": actual,
                        "predicted": predicted,
                        "scores": scores,
                    })

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metrics = calculate_metrics(
        all_true,
        all_pred
    )

    exact_correct = sum(
        true_row == pred_row
        for true_row, pred_row
        in zip(all_true, all_pred)
    )

    exact_match = exact_correct / len(all_true)

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(
        f"Macro Precision: {metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall:    {metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1:        {metrics['macro_f1']:.4f}"
    )

    print(
        f"Micro Precision: {metrics['micro_precision']:.4f}"
    )

    print(
        f"Micro Recall:    {metrics['micro_recall']:.4f}"
    )

    print(
        f"Micro F1:        {metrics['micro_f1']:.4f}"
    )

    print(
        f"Exact Match:     {exact_match:.4f} "
        f"({exact_correct}/{len(all_true)})"
    )

    print()
    print("Per-label results:")
    print("-" * 60)

    for label in LABELS:

        result = metrics["per_label"][label]

        print(
            f"{label:30s} "
            f"P={result['precision']:.4f} "
            f"R={result['recall']:.4f} "
            f"F1={result['f1']:.4f}"
        )

    # --------------------------------------------------------
    # Save evaluation
    # --------------------------------------------------------

    evaluation = {
        "model": "M3 Logician",
        "checkpoint_epoch": checkpoint_epoch,
        "validation_f1": validation_f1,
        "test_examples": len(dataset),
        "threshold": THRESHOLD,
        "metrics": metrics,
        "exact_match": exact_match,
        "exact_correct": exact_correct,
        "incorrect_examples": incorrect,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            evaluation,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        f"Saved evaluation to: {OUTPUT_FILE}"
    )

    print()
    print("=" * 60)
    print("FIRST 20 INCORRECT TEST EXAMPLES")
    print("=" * 60)

    for i, item in enumerate(
        incorrect[:20],
        start=1
    ):

        print()
        print(f"{i}. {item['text']}")
        print(f"   Actual:    {item['actual']}")
        print(f"   Predicted: {item['predicted']}")
        print(f"   Scores:    {item['scores']}")


if __name__ == "__main__":
    main()