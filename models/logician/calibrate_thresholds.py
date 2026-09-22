import json
from pathlib import Path
import torch
from torch.utils.data import DataLoader

from model import LogicianTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VAL_FILE = PROJECT_ROOT / "dataset/logician/logician_v3/val.jsonl"
VOCAB_FILE = PROJECT_ROOT / "models/logician/tokenizer/vocab.json"
CHECKPOINT = PROJECT_ROOT / "checkpoints/logician/best_model.pt"

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
    import re
    return re.findall(
        r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?|[^\w\s]",
        text.lower()
    )


def encode(text, vocab):
    ids = [vocab.get(t, UNK_ID) for t in tokenize(text)]
    ids = ids[:MAX_SEQ_LEN - 2]

    ids = [BOS_ID] + ids + [EOS_ID]
    mask = [1] * len(ids)

    padding = MAX_SEQ_LEN - len(ids)

    if padding > 0:
        ids += [PAD_ID] * padding
        mask += [0] * padding

    return ids, mask


class SimpleDataset(torch.utils.data.Dataset):

    def __init__(self, path, vocab):
        self.data = []

        with open(path, "r", encoding="utf-8-sig") as f:
            for line in f:
                if not line.strip():
                    continue

                item = json.loads(line)

                ids, mask = encode(item["text"], vocab)

                target = torch.zeros(len(LABELS))

                for label in item["labels"]:
                    if label in LABELS:
                        target[LABELS.index(label)] = 1.0

                self.data.append((
                    torch.tensor(ids, dtype=torch.long),
                    torch.tensor(mask, dtype=torch.long),
                    target
                ))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]


def f1_at_threshold(probs, targets, threshold):

    preds = (probs >= threshold).float()

    tp = (preds * targets).sum()
    fp = (preds * (1 - targets)).sum()
    fn = ((1 - preds) * targets).sum()

    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)

    return (
        2 * precision * recall
        / (precision + recall + 1e-8)
    ).item()


def main():

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    with open(VOCAB_FILE, "r", encoding="utf-8-sig") as f:
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

    dataset = SimpleDataset(
        VAL_FILE,
        vocab
    )

    loader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=False
    )

    all_probs = []
    all_targets = []

    with torch.no_grad():

        for ids, masks, targets in loader:

            ids = ids.to(device)
            masks = masks.to(device)

            logits = model(
                ids,
                masks
            )

            probs = torch.sigmoid(logits)

            all_probs.append(probs.cpu())
            all_targets.append(targets)

    probs = torch.cat(all_probs)
    targets = torch.cat(all_targets)

    print("=" * 60)
    print("M3 THRESHOLD CALIBRATION")
    print("=" * 60)

    thresholds = {}

    for i, label in enumerate(LABELS):

        best_threshold = 0.5
        best_f1 = -1

        for threshold in [
            x / 100
            for x in range(10, 91)
        ]:

            score = f1_at_threshold(
                probs[:, i],
                targets[:, i],
                threshold
            )

            if score > best_f1:
                best_f1 = score
                best_threshold = threshold

        thresholds[label] = best_threshold

        print(
            f"{label:28} "
            f"threshold={best_threshold:.2f} "
            f"F1={best_f1:.4f}"
        )

    output = PROJECT_ROOT / "checkpoints/logician/thresholds.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2)

    print()
    print("Saved:", output)


if __name__ == "__main__":
    main()
