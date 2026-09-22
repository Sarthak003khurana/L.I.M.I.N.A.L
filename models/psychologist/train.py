import json
import random
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.amp import GradScaler, autocast

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.psychologist.model import PsychologistModel


# ============================================================
# CONFIGURATION
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

PAD_ID = 0
UNK_ID = 1
BOS_ID = 2
EOS_ID = 3

MAX_SEQUENCE_LENGTH = 128

BATCH_SIZE = 32
EPOCHS = 40

LEARNING_RATE = 3e-4
WEIGHT_DECAY = 1e-4

GRADIENT_CLIP = 1.0

EARLY_STOPPING_PATIENCE = 7

SEED = 42


# ============================================================
# PATHS
# ============================================================

DATASET_DIR = PROJECT_ROOT / "dataset" / "psychologist"

MODEL_DIR = PROJECT_ROOT / "models" / "psychologist"

TOKENIZER_FILE = (
    MODEL_DIR
    / "tokenizer"
    / "vocab.json"
)

TRAIN_FILE = (
    DATASET_DIR
    / "psychologist_v3_train.jsonl"
)

VALIDATION_FILE = (
    DATASET_DIR
    / "psychologist_v3_validation.jsonl"
)

CHECKPOINT_DIR = (
    PROJECT_ROOT
    / "checkpoints"
    / "psychologist"
)


# ============================================================
# TOKENIZATION
# ============================================================

import re


def tokenize(text):
    """
    Same tokenizer used during tokenizer training.
    """

    text = text.lower().strip()

    return re.findall(
        r"\w+|[^\w\s]",
        text,
        flags=re.UNICODE,
    )


def load_vocab():

    with open(
        TOKENIZER_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        vocab = json.load(f)

    return vocab


def encode_text(
    text,
    vocab,
    max_length=MAX_SEQUENCE_LENGTH,
):

    tokens = tokenize(text)

    token_ids = [
        vocab.get(
            token,
            UNK_ID
        )
        for token in tokens
    ]

    # Add BOS and EOS.
    token_ids = (
        [BOS_ID]
        + token_ids
        + [EOS_ID]
    )

    # Truncate while preserving EOS.
    if len(token_ids) > max_length:

        token_ids = (
            token_ids[:max_length - 1]
            + [EOS_ID]
        )

    # Padding.
    padding_length = (
        max_length
        - len(token_ids)
    )

    token_ids += [
        PAD_ID
    ] * padding_length

    return token_ids


# ============================================================
# DATASET
# ============================================================

class PsychologistDataset(Dataset):

    def __init__(
        self,
        file_path,
        vocab,
    ):

        self.examples = []

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:

                if not line.strip():
                    continue

                item = json.loads(line)

                text = item["text"]

                labels = item["labels"]

                encoded = encode_text(
                    text,
                    vocab,
                )

                target = [
                    1.0 if label in labels else 0.0
                    for label in LABELS
                ]

                self.examples.append(
                    {
                        "input_ids": encoded,
                        "labels": target,
                    }
                )

    def __len__(self):

        return len(self.examples)

    def __getitem__(self, index):

        item = self.examples[index]

        return (
            torch.tensor(
                item["input_ids"],
                dtype=torch.long,
            ),
            torch.tensor(
                item["labels"],
                dtype=torch.float32,
            ),
        )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    logits,
    targets,
    threshold=0.5,
):

    probabilities = torch.sigmoid(
        logits
    )

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

    exact_match = (
        predictions == targets
    ).all(dim=1).float().mean().item()

    return (
        macro_precision,
        macro_recall,
        macro_f1,
        exact_match,
    )


# ============================================================
# CLASS WEIGHTS
# ============================================================

def calculate_pos_weights(dataset):

    positive_counts = torch.zeros(
        len(LABELS)
    )

    total = len(dataset)

    for _, targets in dataset:

        positive_counts += targets

    negative_counts = (
        total
        - positive_counts
    )

    pos_weights = (
        negative_counts
        / positive_counts.clamp(min=1.0)
    )

    return pos_weights


# ============================================================
# TRAINING
# ============================================================

def main():

    print("=" * 70)
    print("L.I.M.I.N.A.L. — M2 PSYCHOLOGIST TRAINING")
    print("=" * 70)

    random.seed(SEED)

    torch.manual_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

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

        print(
            f"CUDA: "
            f"{torch.version.cuda}"
        )

    # --------------------------------------------------------
    # Load tokenizer
    # --------------------------------------------------------

    vocab = load_vocab()

    vocab_size = len(vocab)

    print(
        f"\nVocabulary size: "
        f"{vocab_size}"
    )

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    train_dataset = PsychologistDataset(
        TRAIN_FILE,
        vocab,
    )

    validation_dataset = PsychologistDataset(
        VALIDATION_FILE,
        vocab,
    )

    print(
        f"Training examples   : "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation examples : "
        f"{len(validation_dataset)}"
    )

    # --------------------------------------------------------
    # DataLoaders
    # --------------------------------------------------------

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = PsychologistModel(
        vocab_size=vocab_size,
        num_labels=len(LABELS),
        embedding_dimension=256,
        num_attention_heads=8,
        num_transformer_layers=4,
        feed_forward_dimension=1024,
        max_sequence_length=MAX_SEQUENCE_LENGTH,
        dropout=0.1,
    ).to(device)

    parameter_count = sum(
        p.numel()
        for p in model.parameters()
    )

    print(
        f"\nModel parameters: "
        f"{parameter_count:,}"
    )

    # --------------------------------------------------------
    # Class weighting
    # --------------------------------------------------------

    pos_weights = calculate_pos_weights(
        train_dataset
    ).to(device)

    print("\nPositive class weights:")

    for label, weight in zip(
        LABELS,
        pos_weights,
    ):

        print(
            f"  {label:<25} "
            f"{weight.item():.3f}"
        )

    criterion = nn.BCEWithLogitsLoss(
        pos_weight=pos_weights
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=0.5,
        patience=2,
    )

    scaler = GradScaler(
        "cuda",
        enabled=torch.cuda.is_available(),
    )

    # --------------------------------------------------------
    # Checkpoint directory
    # --------------------------------------------------------

    CHECKPOINT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    best_checkpoint = (
        CHECKPOINT_DIR
        / "best_model.pt"
    )

    history_file = (
        CHECKPOINT_DIR
        / "training_history.json"
    )

    history = []

    best_validation_f1 = -1.0

    epochs_without_improvement = 0

    # --------------------------------------------------------
    # Training loop
    # --------------------------------------------------------

    print("\nStarting training...\n")

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        model.train()

        running_loss = 0.0

        all_train_logits = []
        all_train_targets = []

        for input_ids, targets in train_loader:

            input_ids = input_ids.to(
                device,
                non_blocking=True,
            )

            targets = targets.to(
                device,
                non_blocking=True,
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            with autocast(
                "cuda",
                enabled=torch.cuda.is_available(),
            ):

                logits = model(
                    input_ids
                )

                loss = criterion(
                    logits,
                    targets,
                )

            scaler.scale(
                loss
            ).backward()

            scaler.unscale_(
                optimizer
            )

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                GRADIENT_CLIP,
            )

            scaler.step(
                optimizer
            )

            scaler.update()

            running_loss += (
                loss.item()
                * input_ids.size(0)
            )

            all_train_logits.append(
                logits.detach().cpu()
            )

            all_train_targets.append(
                targets.detach().cpu()
            )

        train_loss = (
            running_loss
            / len(train_dataset)
        )

        train_logits = torch.cat(
            all_train_logits
        )

        train_targets = torch.cat(
            all_train_targets
        )

        (
            train_precision,
            train_recall,
            train_f1,
            train_exact,
        ) = calculate_metrics(
            train_logits,
            train_targets,
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        model.eval()

        validation_loss = 0.0

        all_validation_logits = []
        all_validation_targets = []

        with torch.no_grad():

            for input_ids, targets in validation_loader:

                input_ids = input_ids.to(
                    device,
                    non_blocking=True,
                )

                targets = targets.to(
                    device,
                    non_blocking=True,
                )

                with autocast(
                    "cuda",
                    enabled=torch.cuda.is_available(),
                ):

                    logits = model(
                        input_ids
                    )

                    loss = criterion(
                        logits,
                        targets,
                    )

                validation_loss += (
                    loss.item()
                    * input_ids.size(0)
                )

                all_validation_logits.append(
                    logits.cpu()
                )

                all_validation_targets.append(
                    targets.cpu()
                )

        validation_loss /= len(
            validation_dataset
        )

        validation_logits = torch.cat(
            all_validation_logits
        )

        validation_targets = torch.cat(
            all_validation_targets
        )

        (
            validation_precision,
            validation_recall,
            validation_f1,
            validation_exact,
        ) = calculate_metrics(
            validation_logits,
            validation_targets,
        )

        scheduler.step(
            validation_f1
        )

        current_lr = optimizer.param_groups[0]["lr"]

        print(
            f"Epoch {epoch:02d} | "
            f"Train Loss {train_loss:.4f} | "
            f"Train F1 {train_f1:.4f} | "
            f"Val Loss {validation_loss:.4f} | "
            f"Val F1 {validation_f1:.4f} | "
            f"Val Precision {validation_precision:.4f} | "
            f"Val Recall {validation_recall:.4f} | "
            f"Exact {validation_exact:.4f} | "
            f"LR {current_lr:.2e}"
        )

        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_precision": train_precision,
            "train_recall": train_recall,
            "train_f1": train_f1,
            "train_exact_match": train_exact,
            "validation_loss": validation_loss,
            "validation_precision": validation_precision,
            "validation_recall": validation_recall,
            "validation_f1": validation_f1,
            "validation_exact_match": validation_exact,
            "learning_rate": current_lr,
        }

        history.append(
            epoch_record
        )

        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        if validation_f1 > best_validation_f1:

            best_validation_f1 = validation_f1

            epochs_without_improvement = 0

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "vocab_size": vocab_size,
                    "num_labels": len(LABELS),
                    "labels": LABELS,
                    "embedding_dimension": 256,
                    "num_attention_heads": 8,
                    "num_transformer_layers": 4,
                    "feed_forward_dimension": 1024,
                    "max_sequence_length": MAX_SEQUENCE_LENGTH,
                    "dropout": 0.1,
                    "best_validation_f1": best_validation_f1,
                    "epoch": epoch,
                },
                best_checkpoint,
            )

            print(
                f"  ✓ New best checkpoint saved "
                f"(F1={best_validation_f1:.4f})"
            )

        else:

            epochs_without_improvement += 1

        if epochs_without_improvement >= EARLY_STOPPING_PATIENCE:

            print(
                "\nEarly stopping triggered."
            )

            break

    # --------------------------------------------------------
    # Save history
    # --------------------------------------------------------

    with open(
        history_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            history,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # GPU memory
    # --------------------------------------------------------

    if torch.cuda.is_available():

        peak_memory = (
            torch.cuda.max_memory_allocated()
            / (1024 ** 3)
        )

        print(
            f"\nPeak GPU memory: "
            f"{peak_memory:.3f} GB"
        )

    print(
        f"\nBest validation F1: "
        f"{best_validation_f1:.4f}"
    )

    print(
        f"Checkpoint: "
        f"{best_checkpoint}"
    )

    print(
        f"History: "
        f"{history_file}"
    )

    print("\n" + "=" * 70)
    print("M2 PSYCHOLOGIST TRAINING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
