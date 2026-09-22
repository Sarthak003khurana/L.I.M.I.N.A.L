import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

TRAIN_FILE = (
    ROOT
    / "dataset"
    / "logician"
    / "logician_v3"
    / "train_augmented.jsonl"
)

CONTRASTIVE_FILE = (
    ROOT
    / "dataset"
    / "logician"
    / "logician_contrastive_seeds.jsonl"
)

OUTPUT_FILE = (
    ROOT
    / "dataset"
    / "logician"
    / "logician_v3"
    / "train_contrastive.jsonl"
)


def load_jsonl(path):
    examples = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            examples.append(json.loads(line))

    return examples


def main():

    print("=" * 60)
    print("M3 CONTRASTIVE DATA AUGMENTATION")
    print("=" * 60)

    original = load_jsonl(TRAIN_FILE)
    contrastive = load_jsonl(CONTRASTIVE_FILE)

    print(f"Original training examples: {len(original)}")
    print(f"Contrastive examples:       {len(contrastive)}")

    combined = []
    seen = set()

    # Existing training data
    for item in original:

        text = item["text"].strip().lower()

        if text not in seen:

            seen.add(text)
            combined.append(item)

    # New contrastive data
    for index, item in enumerate(contrastive, start=1):

        text = item["text"].strip().lower()

        if text in seen:
            continue

        item = dict(item)

        item["family_id"] = f"contrastive_{index:03d}"

        combined.append(item)
        seen.add(text)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for item in combined:

            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False
                )
                + "\n"
            )

    print()
    print(f"Final training examples: {len(combined)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()