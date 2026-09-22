import json
import sys
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

# Add project root to Python path so imports work when
# running:
# python models\archaeologist\evaluate.py

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from models.archaeologist.model import ArchaeologistModel


# ============================================================
# CONFIGURATION
# ============================================================

TEST_FILE = (
    BASE_DIR
    / "dataset"
    / "archaeologist"
    / "archaeologist_v3_test.jsonl"
)

CHECKPOINT_FILE = (
    BASE_DIR
    / "checkpoints"
    / "archaeologist"
    / "best_model.pt"
)

TOKENIZER_DIR = (
    BASE_DIR
    / "models"
    / "archaeologist"
    / "tokenizer"
)

BATCH_SIZE = 32
MAX_LENGTH = 128
THRESHOLD = 0.5

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
# TOKENIZER
# ============================================================

class SimpleTokenizer:

    def __init__(self, tokenizer_dir):

        vocab_file = tokenizer_dir / "vocab.json"

        with open(vocab_file, "r", encoding="utf-8") as f:
            self.vocab = json.load(f)

        self.pad_id = self.vocab["<PAD>"]
        self.unk_id = self.vocab["<UNK>"]
        self.bos_id = self.vocab["<BOS>"]
        self.eos_id = self.vocab["<EOS>"]

    def encode(self, text, max_length=128):

        tokens = text.lower().strip().split()

        token_ids = [self.bos_id]

        for token in tokens:

            token_ids.append(
                self.vocab.get(
                    token,
                    self.unk_id
                )
            )

        token_ids.append(self.eos_id)

        token_ids = token_ids[:max_length]

        attention_mask = [1] * len(token_ids)

        while len(token_ids) < max_length:

            token_ids.append(
                self.pad_id
            )

            attention_mask.append(0)

        return token_ids, attention_mask


# ============================================================
# DATASET
# ============================================================

class ArchaeologistTestDataset(Dataset):

    def __init__(self, file_path, tokenizer):

        self.examples = []

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                item = json.loads(line)

                text = item["text"]
                labels = item["labels"]

                label_vector = [
                    1.0 if label in labels else 0.0
                    for label in LABELS
                ]

                input_ids, attention_mask = tokenizer.encode(
                    text,
                    MAX_LENGTH
                )

                self.examples.append(
                    {
                        "text": text,
                        "input_ids": input_ids,
                        "attention_mask": attention_mask,
                        "labels": label_vector,
                    }
                )

    def __len__(self):

        return len(self.examples)

    def __getitem__(self, index):

        item = self.examples[index]

        return {
            "input_ids": torch.tensor(
                item["input_ids"],
                dtype=torch.long
            ),
            "attention_mask": torch.tensor(
                item["attention_mask"],
                dtype=torch.long
            ),
            "labels": torch.tensor(
                item["labels"],
                dtype=torch.float32
            ),
            "text": item["text"],
        }


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    y_true,
    y_pred
):

    num_labels = len(LABELS)

    results = {}

    total_tp = 0
    total_fp = 0
    total_fn = 0

    all_precision = []
    all_recall = []
    all_f1 = []

    for i, label in enumerate(LABELS):

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        for j in range(len(y_true)):

            actual = y_true[j][i]
            predicted = y_pred[j][i]

            if actual == 1 and predicted == 1:

                tp += 1

            elif actual == 0 and predicted == 1:

                fp += 1

            elif actual == 1 and predicted == 0:

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
            2 * precision * recall
            / (precision + recall)
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

        total_tp += tp
        total_fp += fp
        total_fn += fn

        all_precision.append(
            precision
        )

        all_recall.append(
            recall
        )

        all_f1.append(
            f1
        )

    # ========================================================
    # MACRO METRICS
    # ========================================================

    macro_precision = (
        sum(all_precision)
        / num_labels
    )

    macro_recall = (
        sum(all_recall)
        / num_labels
    )

    macro_f1 = (
        sum(all_f1)
        / num_labels
    )

    # ========================================================
    # MICRO METRICS
    # ========================================================

    micro_precision = (
        total_tp
        / (total_tp + total_fp)
        if (total_tp + total_fp) > 0
        else 0.0
    )

    micro_recall = (
        total_tp
        / (total_tp + total_fn)
        if (total_tp + total_fn) > 0
        else 0.0
    )

    micro_f1 = (
        2
        * micro_precision
        * micro_recall
        / (micro_precision + micro_recall)
        if (micro_precision + micro_recall) > 0
        else 0.0
    )

    # ========================================================
    # EXACT MATCH
    # ========================================================

    exact_matches = 0

    for actual, predicted in zip(
        y_true,
        y_pred
    ):

        if actual == predicted:

            exact_matches += 1

    exact_match = (
        exact_matches / len(y_true)
        if len(y_true) > 0
        else 0.0
    )

    return {
        "per_label": results,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": micro_f1,
        "exact_match": exact_match,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "L.I.M.I.N.A.L. — "
        "ARCHAEOLOGIST BLIND TEST EVALUATION"
    )
    print("=" * 70)

    # ========================================================
    # DEVICE
    # ========================================================

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"\nDevice: {device}"
    )

    if torch.cuda.is_available():

        print(
            "GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

        print(
            "CUDA: "
            f"{torch.version.cuda}"
        )

    # ========================================================
    # TOKENIZER
    # ========================================================

    print(
        "\nLoading tokenizer..."
    )

    tokenizer = SimpleTokenizer(
        TOKENIZER_DIR
    )

    vocab_size = len(
        tokenizer.vocab
    )

    print(
        f"Vocabulary size: {vocab_size}"
    )

    # ========================================================
    # TEST DATASET
    # ========================================================

    print(
        "\nLoading untouched test dataset..."
    )

    dataset = ArchaeologistTestDataset(
        TEST_FILE,
        tokenizer
    )

    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    print(
        f"Test examples: {len(dataset)}"
    )

    # ========================================================
    # MODEL
    # ========================================================

    print(
        "\nLoading best checkpoint..."
    )

    model = ArchaeologistModel(
        vocab_size=vocab_size,
        num_labels=len(LABELS),
        embedding_dimension=256,
        num_attention_heads=8,
        num_transformer_layers=4,
        feed_forward_dimension=1024,
        max_sequence_length=MAX_LENGTH,
        dropout=0.1
    )

    checkpoint = torch.load(
        CHECKPOINT_FILE,
        map_location=device
    )

    if (
        isinstance(checkpoint, dict)
        and "model_state_dict" in checkpoint
    ):

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

    else:

        model.load_state_dict(
            checkpoint
        )

    model.to(device)

    model.eval()

    print(
        "Checkpoint loaded successfully."
    )

    # ========================================================
    # BLIND EVALUATION
    # ========================================================

    all_true = []
    all_pred = []

    print(
        "\nRunning blind evaluation..."
    )

    with torch.no_grad():

        for batch in dataloader:

            input_ids = batch[
                "input_ids"
            ].to(device)

            attention_mask = batch[
                "attention_mask"
            ].to(device)

            labels = batch[
                "labels"
            ]

            logits = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

            probabilities = torch.sigmoid(
                logits
            )

            predictions = (
                probabilities >= THRESHOLD
            ).int()

            all_true.extend(
                labels
                .int()
                .cpu()
                .tolist()
            )

            all_pred.extend(
                predictions
                .cpu()
                .tolist()
            )

    # ========================================================
    # METRICS
    # ========================================================

    metrics = calculate_metrics(
        all_true,
        all_pred
    )

    # ========================================================
    # OVERALL RESULTS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "OVERALL TEST RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"\nMacro Precision : "
        f"{metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall    : "
        f"{metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1        : "
        f"{metrics['macro_f1']:.4f}"
    )

    print(
        f"\nMicro Precision : "
        f"{metrics['micro_precision']:.4f}"
    )

    print(
        f"Micro Recall    : "
        f"{metrics['micro_recall']:.4f}"
    )

    print(
        f"Micro F1        : "
        f"{metrics['micro_f1']:.4f}"
    )

    print(
        f"\nExact Match     : "
        f"{metrics['exact_match']:.4f}"
    )

    # ========================================================
    # PER LABEL
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "PER-LABEL RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"\n{'LABEL':30}"
        f"{'PRECISION':>12}"
        f"{'RECALL':>12}"
        f"{'F1':>12}"
    )

    print(
        "-" * 70
    )

    for label in LABELS:

        result = metrics[
            "per_label"
        ][label]

        print(
            f"{label:30}"
            f"{result['precision']:>12.4f}"
            f"{result['recall']:>12.4f}"
            f"{result['f1']:>12.4f}"
        )

    # ========================================================
    # CONFUSION COUNTS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "CONFUSION COUNTS"
    )

    print(
        "=" * 70
    )

    for label in LABELS:

        result = metrics[
            "per_label"
        ][label]

        print(
            f"\n{label}"
        )

        print(
            f"  TP: {result['tp']}"
        )

        print(
            f"  FP: {result['fp']}"
        )

        print(
            f"  FN: {result['fn']}"
        )

        print(
            f"  TN: {result['tn']}"
        )

    # ========================================================
    # SAVE REPORT
    # ========================================================

    report_path = (
        BASE_DIR
        / "checkpoints"
        / "archaeologist"
        / "test_evaluation.json"
    )

    report = {
        "model": "Archaeologist",
        "test_file": str(
            TEST_FILE
        ),
        "checkpoint": str(
            CHECKPOINT_FILE
        ),
        "test_examples": len(
            dataset
        ),
        "threshold": THRESHOLD,
        "metrics": metrics,
    }

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=2
        )

    print(
        "\nEvaluation report saved to:"
    )

    print(
        report_path
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "BLIND TEST EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()