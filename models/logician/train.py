import json
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


# --------------------------------------------------
# Project path
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


from models.logician.model import LogicianTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRAIN_FILE = PROJECT_ROOT / "dataset/logician/logician_v3/train_contrastive.jsonl"

VAL_FILE = PROJECT_ROOT / "dataset/logician/logician_v3/val.jsonl"

TEST_FILE = PROJECT_ROOT / "dataset/logician/logician_v3/test.jsonl"

VOCAB_FILE = PROJECT_ROOT / "models/logician/tokenizer/vocab.json"

CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints/logician"
CHECKPOINT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

BEST_MODEL = CHECKPOINT_DIR / "best_model.pt"
HISTORY_FILE = CHECKPOINT_DIR / "training_history.json"

LABELS = [
    "SKIPPED_PREMISE",
    "UNANSWERED_COUNTERARGUMENT",
    "UNSUPPORTED_CONCLUSION",
    "UNSTATED_ASSUMPTION",
    "CONTRADICTION",
    "FALSE_DILEMMA"
]

LABEL_TO_ID = {
    label: i
    for i, label in enumerate(LABELS)
}

PAD_ID = 0
UNK_ID = 1
BOS_ID = 2
EOS_ID = 3

MAX_SEQ_LEN = 128

BATCH_SIZE = 32

MAX_EPOCHS = 40

LEARNING_RATE = 1e-4

WEIGHT_DECAY = 5e-4

EARLY_STOPPING_PATIENCE = 7

GRADIENT_CLIP = 1.0

SEED = 42


# --------------------------------------------------
# Reproducibility
# --------------------------------------------------

torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# --------------------------------------------------
# Tokenizer
# --------------------------------------------------

import re


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

    attention_mask = [1] * len(ids)

    padding_length = (
        MAX_SEQ_LEN - len(ids)
    )

    if padding_length > 0:

        ids += [
            PAD_ID
        ] * padding_length

        attention_mask += [
            0
        ] * padding_length

    return ids, attention_mask


# --------------------------------------------------
# Dataset
# --------------------------------------------------

class LogicianDataset(Dataset):

    def __init__(
        self,
        file_path,
        vocab
    ):

        self.data = []

        with file_path.open(
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                if not line.strip():
                    continue

                item = json.loads(line)

                input_ids, attention_mask = encode(
                    item["text"],
                    vocab
                )

                labels = torch.zeros(
                    len(LABELS),
                    dtype=torch.float32
                )

                for label in item["labels"]:

                    if label in LABEL_TO_ID:

                        labels[
                            LABEL_TO_ID[label]
                        ] = 1.0

                self.data.append(
                    (
                        torch.tensor(
                            input_ids,
                            dtype=torch.long
                        ),
                        torch.tensor(
                            attention_mask,
                            dtype=torch.long
                        ),
                        labels
                    )
                )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


# --------------------------------------------------
# Metrics
# --------------------------------------------------

def calculate_metrics(
    logits,
    targets,
    threshold=0.5
):

    probabilities = torch.sigmoid(
        logits
    )

    predictions = (
        probabilities >= threshold
    ).float()

    tp = (
        predictions * targets
    ).sum(dim=0)

    fp = (
        predictions * (1 - targets)
    ).sum(dim=0)

    fn = (
        (1 - predictions) * targets
    ).sum(dim=0)

    precision = tp / (
        tp + fp + 1e-8
    )

    recall = tp / (
        tp + fn + 1e-8
    )

    f1 = (
        2 * precision * recall
        / (precision + recall + 1e-8)
    )

    macro_precision = precision.mean().item()
    macro_recall = recall.mean().item()
    macro_f1 = f1.mean().item()

    return (
        macro_precision,
        macro_recall,
        macro_f1
    )


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

def evaluate(
    model,
    loader,
    criterion,
    device
):

    model.eval()

    total_loss = 0.0

    all_logits = []
    all_targets = []

    with torch.no_grad():

        for (
            input_ids,
            attention_mask,
            targets
        ) in loader:

            input_ids = input_ids.to(
                device
            )

            attention_mask = attention_mask.to(
                device
            )

            targets = targets.to(
                device
            )

            logits = model(
                input_ids,
                attention_mask
            )

            loss = criterion(
                logits,
                targets
            )

            total_loss += (
                loss.item()
                * input_ids.size(0)
            )

            all_logits.append(
                logits.cpu()
            )

            all_targets.append(
                targets.cpu()
            )

    all_logits = torch.cat(
        all_logits
    )

    all_targets = torch.cat(
        all_targets
    )

    precision, recall, f1 = calculate_metrics(
        all_logits,
        all_targets
    )

    average_loss = (
        total_loss
        / len(loader.dataset)
    )

    return (
        average_loss,
        precision,
        recall,
        f1
    )


# --------------------------------------------------
# Main training
# --------------------------------------------------

def main():

    print("=" * 60)
    print("M3 LOGICIAN TRAINING")
    print("=" * 60)

    # --------------------------------------------------
    # Device
    # --------------------------------------------------

    if torch.cuda.is_available():

        device = torch.device(
            "cuda"
        )

        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

    else:

        device = torch.device(
            "cpu"
        )

        print("WARNING: CUDA unavailable.")

    # --------------------------------------------------
    # Vocabulary
    # --------------------------------------------------

    with VOCAB_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        vocab = json.load(f)

    print(
        f"Vocabulary size: {len(vocab)}"
    )

    # --------------------------------------------------
    # Dataset
    # --------------------------------------------------

    train_dataset = LogicianDataset(
        TRAIN_FILE,
        vocab
    )

    val_dataset = LogicianDataset(
        VAL_FILE,
        vocab
    )

    print(
        f"Training examples: "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation examples: "
        f"{len(val_dataset)}"
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=True
    )

    # --------------------------------------------------
    # Model
    # --------------------------------------------------

    model = LogicianTransformer(
        vocab_size=len(vocab),
        num_labels=len(LABELS)
    ).to(device)

    parameter_count = sum(
        p.numel()
        for p in model.parameters()
        if p.requires_grad
    )

    print(
        f"Trainable parameters: "
        f"{parameter_count:,}"
    )

    # --------------------------------------------------
    # Class weights
    # --------------------------------------------------

    positive_counts = torch.zeros(
        len(LABELS)
    )

    negative_counts = torch.zeros(
        len(LABELS)
    )

    for item in train_dataset:

        labels = item[2]

        positive_counts += labels

        negative_counts += (
            1 - labels
        )

    pos_weight = (
        negative_counts
        / positive_counts.clamp(min=1)
    )

    print("\nPositive class weights:")

    for label, weight in zip(
        LABELS,
        pos_weight
    ):

        print(
            f"  {label:28} "
            f"{weight.item():.3f}"
        )

    pos_weight = pos_weight.to(
        device
    )

    criterion = nn.BCEWithLogitsLoss(
        pos_weight=pos_weight
    )

    # --------------------------------------------------
    # Optimizer
    # --------------------------------------------------

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=0.5,
        patience=2
    )

    # --------------------------------------------------
    # Training state
    # --------------------------------------------------

    best_val_f1 = -1.0

    best_epoch = 0

    patience_counter = 0

    history = []

    if torch.cuda.is_available():

        torch.cuda.reset_peak_memory_stats()

    # --------------------------------------------------
    # Epoch loop
    # --------------------------------------------------

    for epoch in range(
        1,
        MAX_EPOCHS + 1
    ):

        model.train()

        running_loss = 0.0

        all_logits = []
        all_targets = []

        for (
            input_ids,
            attention_mask,
            targets
        ) in train_loader:

            input_ids = input_ids.to(
                device,
                non_blocking=True
            )

            attention_mask = attention_mask.to(
                device,
                non_blocking=True
            )

            targets = targets.to(
                device,
                non_blocking=True
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            logits = model(
                input_ids,
                attention_mask
            )

            loss = criterion(
                logits,
                targets
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                GRADIENT_CLIP
            )

            optimizer.step()

            running_loss += (
                loss.item()
                * input_ids.size(0)
            )

            all_logits.append(
                logits.detach().cpu()
            )

            all_targets.append(
                targets.detach().cpu()
            )

        train_loss = (
            running_loss
            / len(train_dataset)
        )

        train_logits = torch.cat(
            all_logits
        )

        train_targets = torch.cat(
            all_targets
        )

        train_precision, train_recall, train_f1 = calculate_metrics(
            train_logits,
            train_targets
        )

        # Validation.
        (
            val_loss,
            val_precision,
            val_recall,
            val_f1
        ) = evaluate(
            model,
            val_loader,
            criterion,
            device
        )

        scheduler.step(
            val_f1
        )

        current_lr = optimizer.param_groups[0]["lr"]

        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_precision": train_precision,
            "train_recall": train_recall,
            "train_f1": train_f1,
            "val_loss": val_loss,
            "val_precision": val_precision,
            "val_recall": val_recall,
            "val_f1": val_f1,
            "learning_rate": current_lr
        }

        history.append(
            epoch_record
        )

        print(
            f"Epoch {epoch:02d} | "
            f"Train Loss {train_loss:.4f} | "
            f"Train F1 {train_f1:.4f} | "
            f"Val Loss {val_loss:.4f} | "
            f"Val F1 {val_f1:.4f}"
        )

        # --------------------------------------------------
        # Save best checkpoint
        # --------------------------------------------------

        if val_f1 > best_val_f1:

            best_val_f1 = val_f1

            best_epoch = epoch

            patience_counter = 0

            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "vocab_size": len(vocab),
                    "num_labels": len(LABELS),
                    "labels": LABELS,
                    "best_val_f1": best_val_f1
                },
                BEST_MODEL
            )

            print(
                f"  -> New best model saved "
                f"(Val F1: {val_f1:.4f})"
            )

        else:

            patience_counter += 1

            print(
                f"  -> No improvement "
                f"({patience_counter}/"
                f"{EARLY_STOPPING_PATIENCE})"
            )

        # --------------------------------------------------
        # Early stopping
        # --------------------------------------------------

        if (
            patience_counter
            >= EARLY_STOPPING_PATIENCE
        ):

            print(
                "\nEarly stopping triggered."
            )

            break

    # --------------------------------------------------
    # Save history
    # --------------------------------------------------

    with HISTORY_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "best_epoch": best_epoch,
                "best_val_f1": best_val_f1,
                "history": history
            },
            f,
            indent=2
        )

    # --------------------------------------------------
    # GPU statistics
    # --------------------------------------------------

    if torch.cuda.is_available():

        peak_memory = (
            torch.cuda.max_memory_allocated()
            / 1024**3
        )

        print(
            f"\nPeak GPU memory: "
            f"{peak_memory:.3f} GB"
        )

    print("\nTraining complete.")

    print(
        f"Best epoch: {best_epoch}"
    )

    print(
        f"Best validation F1: "
        f"{best_val_f1:.4f}"
    )

    print(
        f"Checkpoint: {BEST_MODEL}"
    )

    print(
        f"History: {HISTORY_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
