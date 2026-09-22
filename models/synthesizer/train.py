import json
import random
import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT))


# ============================================================
# IMPORTS
# ============================================================

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from models.synthesizer.model import (
    SynthesizerModel,
    SYNTHESIZER_LABELS,
    text_to_token_ids,
)


# ============================================================
# PATHS
# ============================================================

TRAIN_FILE = (
    ROOT
    / "dataset"
    / "synthesizer_v2"
    / "train.jsonl"
)

VALIDATION_FILE = (
    ROOT
    / "dataset"
    / "synthesizer_v2"
    / "validation.jsonl"
)

CHECKPOINT_DIR = (
    ROOT
    / "checkpoints"
    / "synthesizer"
)

CHECKPOINT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

BEST_MODEL_FILE = (
    CHECKPOINT_DIR
    / "best_model.pt"
)

HISTORY_FILE = (
    CHECKPOINT_DIR
    / "training_history.json"
)


# ============================================================
# CONFIG
# ============================================================

SEED = 42

BATCH_SIZE = 32

MAX_EPOCHS = 150

LEARNING_RATE = 3e-4

WEIGHT_DECAY = 2e-4

EARLY_STOPPING_PATIENCE = 20

LR_PATIENCE = 6

LR_FACTOR = 0.5

GRADIENT_CLIP = 1.0

DROPOUT = 0.20

HIDDEN_DIM = 96

NUM_CLASSES = 8

INPUT_DIM = 25


# ============================================================
# REPRODUCIBILITY
# ============================================================

def set_seed(seed):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():

        torch.cuda.manual_seed_all(seed)


set_seed(SEED)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# DATASET
# ============================================================

class SynthesizerDataset(Dataset):

    def __init__(
        self,
        path,
    ):

        self.examples = []

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                if line.strip():

                    self.examples.append(
                        json.loads(line)
                    )

        if len(self.examples) == 0:

            raise ValueError(
                f"Dataset is empty: {path}"
            )

        # ----------------------------------------------------
        # Validate dataset
        # ----------------------------------------------------

        for index, item in enumerate(
            self.examples
        ):

            if "features" not in item:

                raise ValueError(
                    f"Example {index} is missing "
                    "'features'."
                )

            if "label_id" not in item:

                raise ValueError(
                    f"Example {index} is missing "
                    "'label_id'."
                )

            if "text" not in item:

                raise ValueError(
                    f"Example {index} is missing "
                    "'text'."
                )

            if len(item["features"]) != INPUT_DIM:

                raise ValueError(
                    f"Example {index} has "
                    f"{len(item['features'])} features. "
                    f"Expected {INPUT_DIM}."
                )

            label_id = int(
                item["label_id"]
            )

            if not (
                0
                <= label_id
                < NUM_CLASSES
            ):

                raise ValueError(
                    f"Invalid label_id "
                    f"{label_id} at example "
                    f"{index}."
                )

    def __len__(self):

        return len(
            self.examples
        )

    def __getitem__(
        self,
        index,
    ):

        item = self.examples[
            index
        ]

        features = torch.tensor(
            item["features"],
            dtype=torch.float32,
        )

        label = torch.tensor(
            item["label_id"],
            dtype=torch.long,
        )

        token_ids = text_to_token_ids(
            item["text"]
        )

        return (
            features,
            token_ids,
            label,
        )


# ============================================================
# COLLATE
# ============================================================

def collate_batch(
    batch,
):

    features = torch.stack(
        [
            item[0]
            for item in batch
        ]
    )

    token_ids = [
        item[1]
        for item in batch
    ]

    labels = torch.stack(
        [
            item[2]
            for item in batch
        ]
    )

    return (
        features,
        token_ids,
        labels,
    )


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(
    path,
):

    return SynthesizerDataset(
        path
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    predictions,
    labels,
    num_classes,
):

    predictions = np.asarray(
        predictions
    )

    labels = np.asarray(
        labels
    )

    precision_values = []

    recall_values = []

    f1_values = []

    for class_id in range(
        num_classes
    ):

        tp = np.sum(
            (
                predictions == class_id
            )
            &
            (
                labels == class_id
            )
        )

        fp = np.sum(
            (
                predictions == class_id
            )
            &
            (
                labels != class_id
            )
        )

        fn = np.sum(
            (
                predictions != class_id
            )
            &
            (
                labels == class_id
            )
        )

        precision = (
            tp
            / (tp + fp)
            if tp + fp > 0
            else 0.0
        )

        recall = (
            tp
            / (tp + fn)
            if tp + fn > 0
            else 0.0
        )

        if (
            precision + recall
        ) > 0:

            f1 = (
                2
                * precision
                * recall
                / (
                    precision
                    + recall
                )
            )

        else:

            f1 = 0.0

        precision_values.append(
            precision
        )

        recall_values.append(
            recall
        )

        f1_values.append(
            f1
        )

    accuracy = float(
        np.mean(
            predictions == labels
        )
    )

    return {
        "accuracy": accuracy,

        "macro_precision": float(
            np.mean(
                precision_values
            )
        ),

        "macro_recall": float(
            np.mean(
                recall_values
            )
        ),

        "macro_f1": float(
            np.mean(
                f1_values
            )
        ),

        "precision_per_class":
            precision_values,

        "recall_per_class":
            recall_values,

        "f1_per_class":
            f1_values,
    }


# ============================================================
# RUN EPOCH
# ============================================================

def run_epoch(
    model,
    loader,
    criterion,
    optimizer=None,
):

    training = optimizer is not None

    if training:

        model.train()

    else:

        model.eval()

    total_loss = 0.0

    all_predictions = []

    all_labels = []

    for (
        features,
        token_ids,
        labels,
    ) in loader:

        features = features.to(
            DEVICE,
            non_blocking=True,
        )

        labels = labels.to(
            DEVICE,
            non_blocking=True,
        )

        if training:

            optimizer.zero_grad(
                set_to_none=True
            )

        with torch.set_grad_enabled(
            training
        ):

            output = model(
                features,
                token_ids,
            )

            logits = output[
                "subtext_logits"
            ]

            loss = criterion(
                logits,
                labels,
            )

            if training:

                loss.backward()

                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    GRADIENT_CLIP,
                )

                optimizer.step()

        total_loss += (
            loss.item()
            * features.size(0)
        )

        predictions = torch.argmax(
            logits,
            dim=1,
        )

        all_predictions.extend(
            predictions.detach()
            .cpu()
            .tolist()
        )

        all_labels.extend(
            labels.detach()
            .cpu()
            .tolist()
        )

    average_loss = (
        total_loss
        / len(loader.dataset)
    )

    metrics = calculate_metrics(
        all_predictions,
        all_labels,
        NUM_CLASSES,
    )

    return (
        average_loss,
        metrics,
    )


# ============================================================
# SAVE CHECKPOINT
# ============================================================

def save_checkpoint(
    model,
    optimizer,
    scheduler,
    epoch,
    metrics,
):

    checkpoint = {

        "model_state_dict":
            model.state_dict(),

        "optimizer_state_dict":
            optimizer.state_dict(),

        "scheduler_state_dict":
            scheduler.state_dict(),

        "epoch":
            epoch,

        "metrics":
            metrics,

        "metadata":
            {
                "input_dim":
                    INPUT_DIM,

                "hidden_dim":
                    HIDDEN_DIM,

                "num_classes":
                    NUM_CLASSES,

                "dropout":
                    DROPOUT,

                "text_encoder":
                    True,

                "text_buckets":
                    256,

                "max_text_tokens":
                    64,

                "architecture":
                    "text_plus_agent_fusion_v1",

                "dataset":
                    "synthesizer_v2",

                "seed":
                    SEED,
            },
    }

    torch.save(
        checkpoint,
        BEST_MODEL_FILE,
    )


# ============================================================
# PRINT METRICS
# ============================================================

def print_metrics(
    prefix,
    loss,
    metrics,
):

    print(
        f"{prefix} | "
        f"Loss {loss:.4f} | "
        f"Acc {metrics['accuracy']:.4f} | "
        f"Macro P {metrics['macro_precision']:.4f} | "
        f"Macro R {metrics['macro_recall']:.4f} | "
        f"Macro F1 {metrics['macro_f1']:.4f}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 70
    )

    print(
        "L.I.M.I.N.A.L. M5 V2 TEXT-AWARE TRAINING"
    )

    print(
        "=" * 70
    )

    print(
        f"\nDevice: {DEVICE}"
    )

    if torch.cuda.is_available():

        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

        print(
            f"CUDA: "
            f"{torch.version.cuda}"
        )

    print(
        f"Random seed: {SEED}"
    )

    print(
        f"Batch size: {BATCH_SIZE}"
    )

    print(
        f"Max epochs: {MAX_EPOCHS}"
    )

    print(
        f"Learning rate: {LEARNING_RATE}"
    )

    print(
        f"Weight decay: {WEIGHT_DECAY}"
    )

    print(
        f"Text buckets: 256"
    )

    print(
        f"Text max tokens: 64"
    )

    print(
        "\nM5 input:"
    )

    print(
        "  25 production M1-M4 features"
    )

    print(
        "  + from-scratch text encoder"
    )

    print(
        "  + trainable fusion"
    )

    # --------------------------------------------------------
    # Verify paths
    # --------------------------------------------------------

    print(
        "\nDataset paths:"
    )

    print(
        f"  Train: {TRAIN_FILE}"
    )

    print(
        f"  Validation: {VALIDATION_FILE}"
    )

    if not TRAIN_FILE.exists():

        raise FileNotFoundError(
            f"\nTraining dataset not found:\n"
            f"{TRAIN_FILE}"
        )

    if not VALIDATION_FILE.exists():

        raise FileNotFoundError(
            f"\nValidation dataset not found:\n"
            f"{VALIDATION_FILE}"
        )

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    print(
        "\nLoading V2 datasets..."
    )

    train_dataset = load_dataset(
        TRAIN_FILE
    )

    validation_dataset = load_dataset(
        VALIDATION_FILE
    )

    print(
        f"Training examples: "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation examples: "
        f"{len(validation_dataset)}"
    )

    # --------------------------------------------------------
    # Data loaders
    # --------------------------------------------------------

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=collate_batch,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collate_batch,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print(
        "\nInitializing M5 V2 model..."
    )

    model = SynthesizerModel(
        input_dim=INPUT_DIM,
        hidden_dim=HIDDEN_DIM,
        num_classes=NUM_CLASSES,
        dropout=DROPOUT,
    ).to(
        DEVICE
    )

    total_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    print(
        f"Total parameters: "
        f"{total_parameters:,}"
    )

    print(
        f"Trainable parameters: "
        f"{trainable_parameters:,}"
    )

    # --------------------------------------------------------
    # Optimizer
    # --------------------------------------------------------

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=LR_FACTOR,
        patience=LR_PATIENCE,
        min_lr=1e-6,
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "STARTING M5 V2 TRAINING"
    )

    print(
        "=" * 70
    )

    best_f1 = -1.0

    epochs_without_improvement = 0

    history = []

    for epoch in range(
        1,
        MAX_EPOCHS + 1,
    ):

        print(
            f"\nEpoch {epoch:03d}"
        )

        train_loss, train_metrics = (
            run_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
            )
        )

        val_loss, val_metrics = (
            run_epoch(
                model,
                validation_loader,
                criterion,
            )
        )

        print_metrics(
            "TRAIN",
            train_loss,
            train_metrics,
        )

        print_metrics(
            "VAL  ",
            val_loss,
            val_metrics,
        )

        current_lr = optimizer.param_groups[
            0
        ][
            "lr"
        ]

        print(
            f"Learning rate: "
            f"{current_lr:.2e}"
        )

        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "train": train_metrics,
                "validation": val_metrics,
                "learning_rate": current_lr,
            }
        )

        # ----------------------------------------------------
        # Save best checkpoint
        # ----------------------------------------------------

        if (
            val_metrics["macro_f1"]
            > best_f1
        ):

            best_f1 = (
                val_metrics[
                    "macro_f1"
                ]
            )

            epochs_without_improvement = 0

            save_checkpoint(
                model,
                optimizer,
                scheduler,
                epoch,
                val_metrics,
            )

            print(
                f"  ✓ Saved best model "
                f"(Val Macro F1: "
                f"{best_f1:.4f})"
            )

        else:

            epochs_without_improvement += 1

            print(
                f"  No improvement "
                f"({epochs_without_improvement}/"
                f"{EARLY_STOPPING_PATIENCE})"
            )

        # ----------------------------------------------------
        # Learning-rate scheduler
        # ----------------------------------------------------

        scheduler.step(
            val_metrics["macro_f1"]
        )

        # ----------------------------------------------------
        # Early stopping
        # ----------------------------------------------------

        if (
            epochs_without_improvement
            >= EARLY_STOPPING_PATIENCE
        ):

            print(
                f"\nEarly stopping at "
                f"epoch {epoch}."
            )

            break

    # --------------------------------------------------------
    # Save history
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Best checkpoint metrics
    # --------------------------------------------------------

    checkpoint = torch.load(
        BEST_MODEL_FILE,
        map_location="cpu",
        weights_only=False,
    )

    best_metrics = checkpoint[
        "metrics"
    ]

    best_epoch = checkpoint.get(
        "epoch",
        None
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "M5 V2 TRAINING COMPLETE"
    )

    print(
        "=" * 70
    )

    if best_epoch is not None:

        print(
            f"Best epoch              : "
            f"{best_epoch}"
        )

    print(
        f"Best validation accuracy : "
        f"{best_metrics['accuracy']:.4f}"
    )

    print(
        f"Best validation Macro P  : "
        f"{best_metrics['macro_precision']:.4f}"
    )

    print(
        f"Best validation Macro R  : "
        f"{best_metrics['macro_recall']:.4f}"
    )

    print(
        f"Best validation Macro F1 : "
        f"{best_metrics['macro_f1']:.4f}"
    )

    # --------------------------------------------------------
    # Per-class metrics
    # --------------------------------------------------------

    print(
        "\nPer-class validation metrics:"
    )

    print(
        f"{'Class':<35}"
        f"{'Precision':>12}"
        f"{'Recall':>10}"
        f"{'F1':>10}"
    )

    print(
        "-" * 70
    )

    for index, label in enumerate(
        SYNTHESIZER_LABELS
    ):

        precision = best_metrics[
            "precision_per_class"
        ][index]

        recall = best_metrics[
            "recall_per_class"
        ][index]

        f1 = best_metrics[
            "f1_per_class"
        ][index]

        print(
            f"{label:<35}"
            f"{precision:>12.4f}"
            f"{recall:>10.4f}"
            f"{f1:>10.4f}"
        )

    # --------------------------------------------------------
    # Files
    # --------------------------------------------------------

    print(
        "\nCheckpoint:"
    )

    print(
        BEST_MODEL_FILE
    )

    print(
        "\nHistory:"
    )

    print(
        HISTORY_FILE
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "The blind TEST set was not used."
    )

    print(
        "Do not evaluate the blind test yet."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()