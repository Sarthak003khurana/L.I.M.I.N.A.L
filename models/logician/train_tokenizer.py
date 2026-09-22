import json
from pathlib import Path
from collections import Counter
import re

TRAIN_PATH = Path("dataset/logician/logician_v3/train_augmented.jsonl")
TOKENIZER_DIR = Path("models/logician/tokenizer")

SPECIAL_TOKENS = ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]


def tokenize(text):
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def main():
    rows = []

    with open(TRAIN_PATH, "r", encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    counter = Counter()

    for row in rows:
        counter.update(tokenize(row["text"]))

    vocab = {}

    for token in SPECIAL_TOKENS:
        vocab[token] = len(vocab)

    for token, _ in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        if token not in vocab:
            vocab[token] = len(vocab)

    TOKENIZER_DIR.mkdir(parents=True, exist_ok=True)

    with open(TOKENIZER_DIR / "vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)

    config = {
        "tokenizer_type": "custom_word_tokenizer",
        "lowercase": True,
        "special_tokens": SPECIAL_TOKENS,
        "vocab_size": len(vocab),
        "training_examples": len(rows)
    }

    with open(TOKENIZER_DIR / "tokenizer_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print("Training examples:", len(rows))
    print("Unique tokens:", len(vocab) - len(SPECIAL_TOKENS))
    print("Vocabulary size:", len(vocab))
    print("Saved tokenizer to:", TOKENIZER_DIR)


if __name__ == "__main__":
    main()
