import json
import math
import random
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.amp import GradScaler, autocast
# Import our randomly initialized Archaeologist architecture.
from model import ArchaeologistModel


# ============================================================
# L.I.M.I.N.A.L. — ARCHAEOLOGIST TRAINING
# ============================================================

SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent.parent

DATASET_DIR = (
    PROJECT_DIR
    / "dataset"
    / "archaeologist"
)

TOKENIZER_DIR = (
    BASE_DIR
    / "tokenizer"
)

VOCAB_FILE = (
    TOKENIZER_DIR
    / "vocab.json"
)

TRAIN_FILE = (
    DATASET_DIR
    / "archaeologist_v3_train.jsonl"
)

VALIDATION_FILE = (
    DATASET_DIR
    / "archaeologist_v3_validation.jsonl"
)

CHECKPOINT_DIR = (
    PROJECT_DIR
    / "checkpoints"
    / "archaeologist"
)

CHECKPOINT_FILE = (
    CHECKPOINT_DIR
    / "best_model.pt"
)

HISTORY_FILE = (
    CHECKPOINT_DIR
    / "training_history.json"
)


# ============================================================
# LABELS
# ============================================================

LABELS = [
    "NO_OMISSION",
    "HEDGING",
    "MISSING_ACTOR",
    "PASSIVE_CONSTRUCTION",
    "MISSING_COMMITMENT",
    "VAGUE_REFERENCE",
    "RESPONSIBILITY_AVOIDANCE",
]

LABEL_TO_ID = {
    label: index
    for index, label in enumerate(LABELS)
}


# ============================================================
# TRAINING CONFIGURATION
# ============================================================

MAX_SEQUENCE_LENGTH = 128

BATCH_SIZE = 32

EPOCHS = 30

LEARNING_RATE = 3e-4

WEIGHT_DECAY = 1e-4

DROPOUT = 0.1

NUM_WORKERS = 0

GRADIENT_CLIP = 1.0

EARLY_STOPPING_PATIENCE = 6

DECISION_THRESHOLD = 0.5


# ============================================================
# TOKENIZER
# ============================================================

def tokenize(text):

    text = text.lower()

    tokens = []

    current = ""

    for character in text:

        if character.isalnum() or character == "'":

            current += character

        else:

            if current:
                tokens.append(current)
                current = ""

            if character in ".,!?;:()-":

                tokens.append(character)

    if current:
        tokens.append(current)

    return tokens


def encode_text(
    text,
    vocabulary,
    max_length=MAX_SEQUENCE_LENGTH,
):

    tokens = tokenize(text)

    pad_id = vocabulary["<PAD>"]
    unk_id = vocabulary["<UNK>"]
    bos_id = vocabulary["<BOS>"]
    eos_id = vocabulary["<EOS>"]

    ids = [bos_id]

    for token in tokens:

        ids.append(
            vocabulary.get(
                token,
                unk_id,
            )
        )

    ids.append(eos_id)

    # Truncate while preserving the maximum length.
    ids = ids[:max_length]

    attention_mask = [
        1
        for _ in ids
    ]

    while len(ids) < max_length:

        ids.append(pad_id)
        attention_mask.append(0)

    return ids, attention_mask


# ============================================================
# DATASET
# ============================================================

class ArchaeologistDataset(Dataset):

    def __init__(
        self,
        file_path,
        vocabulary,
    ):

        self.examples = []

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                example = json.loads(line)

                input_ids, attention_mask = encode_text(
                    example["text"],
                    vocabulary,
                )

                labels = torch.zeros(
                    len(LABELS),
                    dtype=torch.float32,
                )

                for label in example.get(
                    "labels",
                    [],
                ):

                    if label in LABEL_TO_ID:

                        labels[
                            LABEL_TO_ID[label]
                        ] = 1.0

                self.examples.append(
                    {
                        "input_ids": input_ids,
                        "attention_mask": attention_mask,
                        "labels": labels,
                    }
                )

    def __len__(self):

        return len(self.examples)

    def __getitem__(self, index):

        example = self.examples[index]

        return {
            "input_ids": torch.tensor(
                example["input_ids"],
                dtype=torch.long,
            ),
            "attention_mask": torch.tensor(
                example["attention_mask"],
                dtype=torch.long,
            ),
            "labels": example["labels"],
        }


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    logits,
    targets,
    threshold=DECISION_THRESHOLD,
):

    probabilities = torch.sigmoid(
        logits
    )

    predictions = (
        probabilities >= threshold
    ).float()

    targets = targets.float()

    true_positive = (
        predictions * targets
    ).sum()

    false_positive = (
        predictions * (1.0 - targets)
    ).sum()

    false_negative = (
        (1.0 - predictions) * targets
    ).sum()

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
        2.0
        * precision
        * recall
        / (
            precision
            + recall
            + 1e-8
        )
    )

    exact_matches = (
        predictions == targets
    ).all(dim=1)

    exact_match_accuracy = (
        exact_matches.float().mean()
    )

    return {
        "precision": precision.item(),
        "recall": recall.item(),
        "f1": f1.item(),
        "exact_match_accuracy": (
            exact_match_accuracy.item()
        ),
    }


# ============================================================
# PER-LABEL METRICS
# ============================================================

def calculate_per_label_metrics(
    logits,
    targets,
    threshold=DECISION_THRESHOLD,
):

    probabilities = torch.sigmoid(
        logits
    )

    predictions = (
        probabilities >= threshold
    ).float()

    results = {}

    for index, label in enumerate(LABELS):

        pred = predictions[:, index]

        target = targets[:, index]

        tp = (
            pred * target
        ).sum()

        fp = (
            pred * (1.0 - target)
        ).sum()

        fn = (
            (1.0 - pred) * target
        ).sum()

        precision = (
            tp
            / (
                tp
                + fp
                + 1e-8
            )
        )

        recall = (
            tp
            / (
                tp
                + fn
                + 1e-8
            )
        )

        f1 = (
            2.0
            * precision
            * recall
            / (
                precision
                + recall
                + 1e-8
            )
        )

        results[label] = {
            "precision": precision.item(),
            "recall": recall.item(),
            "f1": f1.item(),
        }

    return results


# ============================================================
# CLASS WEIGHTS
# ============================================================

def calculate_pos_weights(dataset):

    positive_counts = torch.zeros(
        len(LABELS),
        dtype=torch.float32,
    )

    negative_counts = torch.zeros(
        len(LABELS),
        dtype=torch.float32,
    )

    for example in dataset.examples:

        labels = example["labels"]

        positive_counts += labels

        negative_counts += (
            1.0 - labels
        )

    pos_weights = (
        negative_counts
        / positive_counts.clamp(
            min=1.0
        )
    )

    return pos_weights


# ============================================================
# TRAIN ONE EPOCH
# ============================================================

def train_one_epoch(
    model,
    loader,
    optimizer,
    criterion,
    scaler,
    device,
):

    model.train()

    total_loss = 0.0

    all_logits = []
    all_targets = []

    for batch in loader:

        input_ids = batch[
            "input_ids"
        ].to(device)

        attention_mask = batch[
            "attention_mask"
        ].to(device)

        targets = batch[
            "labels"
        ].to(device)

        optimizer.zero_grad(
            set_to_none=True
        )

        with autocast(
            "cuda",
            dtype=torch.float16,
            enabled=device.type == "cuda",
        ):

            logits = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
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

        total_loss += (
            loss.item()
            * input_ids.size(0)
        )

        all_logits.append(
            logits.detach().float().cpu()
        )

        all_targets.append(
            targets.detach().float().cpu()
        )

    average_loss = (
        total_loss
        / len(loader.dataset)
    )

    all_logits = torch.cat(
        all_logits,
        dim=0,
    )

    all_targets = torch.cat(
        all_targets,
        dim=0,
    )

    metrics = calculate_metrics(
        all_logits,
        all_targets,
    )

    return average_loss, metrics


# ============================================================
# VALIDATION
# ============================================================

@torch.no_grad()
def validate(
    model,
    loader,
    criterion,
    device,
):

    model.eval()

    total_loss = 0.0

    all_logits = []
    all_targets = []

    for batch in loader:

        input_ids = batch[
            "input_ids"
        ].to(device)

        attention_mask = batch[
            "attention_mask"
        ].to(device)

        targets = batch[
            "labels"
        ].to(device)

        with autocast(
            device_type="cuda",
            dtype=torch.float16,
            enabled=device.type == "cuda",
        ):

            logits = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )

            loss = criterion(
                logits,
                targets,
            )

        total_loss += (
            loss.item()
            * input_ids.size(0)
        )

        all_logits.append(
            logits.detach().float().cpu()
        )

        all_targets.append(
            targets.detach().float().cpu()
        )

    average_loss = (
        total_loss
        / len(loader.dataset)
    )

    all_logits = torch.cat(
        all_logits,
        dim=0,
    )

    all_targets = torch.cat(
        all_targets,
        dim=0,
    )

    metrics = calculate_metrics(
        all_logits,
        all_targets,
    )

    per_label = calculate_per_label_metrics(
        all_logits,
        all_targets,
    )

    return (
        average_loss,
        metrics,
        per_label,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("L.I.M.I.N.A.L. — ARCHAEOLOGIST TRAINING")
    print("=" * 70)

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print()
    print(
        f"Device : {device}"
    )

    if device.type == "cuda":

        print(
            f"GPU    : "
            f"{torch.cuda.get_device_name(0)}"
        )

        print(
            f"CUDA   : "
            f"{torch.version.cuda}"
        )

    # --------------------------------------------------------
    # Load vocabulary
    # --------------------------------------------------------

    if not VOCAB_FILE.exists():

        raise FileNotFoundError(
            f"Vocabulary not found: {VOCAB_FILE}"
        )

    with open(
        VOCAB_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        vocabulary = json.load(file)

    print()
    print(
        f"Vocabulary size : "
        f"{len(vocabulary)}"
    )

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    if not TRAIN_FILE.exists():

        raise FileNotFoundError(
            f"Training dataset not found: {TRAIN_FILE}"
        )

    if not VALIDATION_FILE.exists():

        raise FileNotFoundError(
            f"Validation dataset not found: {VALIDATION_FILE}"
        )

    train_dataset = ArchaeologistDataset(
        TRAIN_FILE,
        vocabulary,
    )

    validation_dataset = ArchaeologistDataset(
        VALIDATION_FILE,
        vocabulary,
    )

    print()
    print(
        f"Training examples   : "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation examples : "
        f"{len(validation_dataset)}"
    )

    # --------------------------------------------------------
    # Data loaders
    # --------------------------------------------------------

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=device.type == "cuda",
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=device.type == "cuda",
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = ArchaeologistModel(
        vocab_size=len(vocabulary),
        num_labels=len(LABELS),
        embedding_dimension=256,
        num_attention_heads=8,
        num_transformer_layers=4,
        feed_forward_dimension=1024,
        max_sequence_length=MAX_SEQUENCE_LENGTH,
        dropout=DROPOUT,
    )

    model = model.to(device)

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print()
    print(
        f"Model parameters : "
        f"{parameter_count:,}"
    )

    # --------------------------------------------------------
    # Class weights
    # --------------------------------------------------------

    pos_weights = calculate_pos_weights(
        train_dataset
    )

    pos_weights = pos_weights.to(
        device
    )

    print()
    print("Positive class weights:")

    for label, weight in zip(
        LABELS,
        pos_weights.detach().cpu().tolist(),
    ):

        print(
            f"  {label:<28} "
            f"{weight:.3f}"
        )

    # --------------------------------------------------------
    # Loss
    # --------------------------------------------------------

    criterion = nn.BCEWithLogitsLoss(
        pos_weight=pos_weights
    )

    # --------------------------------------------------------
    # Optimizer
    # --------------------------------------------------------

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    # --------------------------------------------------------
    # Learning-rate scheduler
    # --------------------------------------------------------

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=0.5,
        patience=2,
        min_lr=1e-6,
    )

    # --------------------------------------------------------
    # Mixed precision
    # --------------------------------------------------------

    scaler = GradScaler(
    "cuda",
    enabled=device.type == "cuda",
    )

    # --------------------------------------------------------
    # Checkpoint directory
    # --------------------------------------------------------

    CHECKPOINT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    best_validation_f1 = -1.0

    epochs_without_improvement = 0

    history = []

    print()
    print("=" * 70)
    print("TRAINING START")
    print("=" * 70)

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        epoch_start = time.time()

        train_loss, train_metrics = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            scaler=scaler,
            device=device,
        )

        validation_loss, validation_metrics, per_label = validate(
            model=model,
            loader=validation_loader,
            criterion=criterion,
            device=device,
        )

        scheduler.step(
            validation_metrics["f1"]
        )

        current_lr = optimizer.param_groups[0][
            "lr"
        ]

        epoch_time = (
            time.time()
            - epoch_start
        )

        print()
        print(
            f"Epoch {epoch:02d}/{EPOCHS}"
        )

        print(
            f"  Train Loss : "
            f"{train_loss:.4f}"
        )

        print(
            f"  Train F1   : "
            f"{train_metrics['f1']:.4f}"
        )

        print(
            f"  Val Loss   : "
            f"{validation_loss:.4f}"
        )

        print(
            f"  Val F1     : "
            f"{validation_metrics['f1']:.4f}"
        )

        print(
            f"  Val Prec   : "
            f"{validation_metrics['precision']:.4f}"
        )

        print(
            f"  Val Recall  : "
            f"{validation_metrics['recall']:.4f}"
        )

        print(
            f"  Exact Match: "
            f"{validation_metrics['exact_match_accuracy']:.4f}"
        )

        print(
            f"  LR         : "
            f"{current_lr:.6f}"
        )

        print(
            f"  Time       : "
            f"{epoch_time:.2f}s"
        )

        # ----------------------------------------------------
        # Per-label validation F1
        # ----------------------------------------------------

        print()
        print("  Per-label F1:")

        for label in LABELS:

            print(
                f"    {label:<28} "
                f"{per_label[label]['f1']:.4f}"
            )

        # ----------------------------------------------------
        # Save history
        # ----------------------------------------------------

        history_entry = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_f1": train_metrics["f1"],
            "validation_loss": validation_loss,
            "validation_f1": validation_metrics["f1"],
            "validation_precision": validation_metrics[
                "precision"
            ],
            "validation_recall": validation_metrics[
                "recall"
            ],
            "validation_exact_match": validation_metrics[
                "exact_match_accuracy"
            ],
            "learning_rate": current_lr,
            "epoch_time_seconds": epoch_time,
            "per_label": per_label,
        }

        history.append(
            history_entry
        )

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                history,
                file,
                indent=2,
            )

        # ----------------------------------------------------
        # Best checkpoint
        # ----------------------------------------------------

        if (
            validation_metrics["f1"]
            > best_validation_f1
        ):

            best_validation_f1 = (
                validation_metrics["f1"]
            )

            epochs_without_improvement = 0

            checkpoint = {

                "epoch": epoch,

                "model_state_dict":
                    model.state_dict(),

                "optimizer_state_dict":
                    optimizer.state_dict(),

                "scheduler_state_dict":
                    scheduler.state_dict(),

                "best_validation_f1":
                    best_validation_f1,

                "vocab_size":
                    len(vocabulary),

                "num_labels":
                    len(LABELS),

                "labels":
                    LABELS,

                "max_sequence_length":
                    MAX_SEQUENCE_LENGTH,

                "embedding_dimension":
                    256,

                "num_attention_heads":
                    8,

                "num_transformer_layers":
                    4,

                "feed_forward_dimension":
                    1024,

                "dropout":
                    DROPOUT,

                "trained_from_scratch":
                    True,

                "pretrained_weights":
                    False,
            }

            torch.save(
                checkpoint,
                CHECKPOINT_FILE,
            )

            print()
            print(
                "  ★ NEW BEST MODEL SAVED"
            )

            print(
                f"    Validation F1: "
                f"{best_validation_f1:.4f}"
            )

        else:

            epochs_without_improvement += 1

            print()
            print(
                f"  No improvement "
                f"({epochs_without_improvement}/"
                f"{EARLY_STOPPING_PATIENCE})"
            )

        # ----------------------------------------------------
        # Early stopping
        # ----------------------------------------------------

        if (
            epochs_without_improvement
            >= EARLY_STOPPING_PATIENCE
        ):

            print()
            print(
                "Early stopping triggered."
            )

            break

    # --------------------------------------------------------
    # Training complete
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Best validation F1 : "
        f"{best_validation_f1:.4f}"
    )

    print()
    print("Best checkpoint:")
    print(CHECKPOINT_FILE)

    print()
    print("Training history:")
    print(HISTORY_FILE)

    if device.type == "cuda":

        torch.cuda.synchronize()

        peak_memory = (
            torch.cuda.max_memory_allocated()
            / (1024 ** 3)
        )

        print()
        print(
            f"Peak GPU memory : "
            f"{peak_memory:.3f} GB"
        )

    print()
    print("=" * 70)
    print("ARCHAEOLOGIST TRAINING FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()