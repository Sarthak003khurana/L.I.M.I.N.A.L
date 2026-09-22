import json
import re
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAIN_FILE = PROJECT_ROOT / "dataset" / "psychologist" / "psychologist_v3_train.jsonl"
TOKENIZER_DIR = PROJECT_ROOT / "models" / "psychologist" / "tokenizer"

SPECIAL_TOKENS = [
    "<PAD>",
    "<UNK>",
    "<BOS>",
    "<EOS>",
]


def tokenize(text):
    text = text.lower().strip()
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def main():
    print("=" * 70)
    print("L.I.M.I.N.A.L. — PSYCHOLOGIST TOKENIZER TRAINING")
    print("=" * 70)

    TOKENIZER_DIR.mkdir(parents=True, exist_ok=True)

    if not TRAIN_FILE.exists():
        raise FileNotFoundError(f"Training file not found: {TRAIN_FILE}")

    counter = Counter()
    examples = 0

    with open(TRAIN_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            item = json.loads(line)
            tokens = tokenize(item["text"])
            counter.update(tokens)
            examples += 1

    print(f"\nTraining examples : {examples}")
    print(f"Unique tokens     : {len(counter)}")

    vocab = {}

    for token in SPECIAL_TOKENS:
        vocab[token] = len(vocab)

    for token, _ in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        if token not in vocab:
            vocab[token] = len(vocab)

    vocab_path = TOKENIZER_DIR / "vocab.json"

    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)

    config = {
        "tokenizer_type": "custom_word_tokenizer",
        "trained_from_scratch": True,
        "lowercase": True,
        "special_tokens": SPECIAL_TOKENS,
        "pad_token": "<PAD>",
        "unk_token": "<UNK>",
        "bos_token": "<BOS>",
        "eos_token": "<EOS>",
        "vocab_size": len(vocab),
        "training_examples": examples
    }

    config_path = TOKENIZER_DIR / "tokenizer_config.json"

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\nVocabulary size   : {len(vocab)}")
    print(f"Vocabulary saved  : {vocab_path}")
    print(f"Config saved      : {config_path}")

    print("\nMost common tokens:")
    for token, count in counter.most_common(20):
        print(f"  {token:<20} {count}")

    print("\nTokenizer verification:")

    test_sentences = [
        "I'm fine with whatever you decide.",
        "That is completely okay, don't worry about it.",
        "I appreciate your effort, but it's your decision."
    ]

    for sentence in test_sentences:
        tokens = tokenize(sentence)
        ids = [vocab.get(token, vocab["<UNK>"]) for token in tokens]

        print(f"\nText   : {sentence}")
        print(f"Tokens : {tokens}")
        print(f"IDs    : {ids}")

    print("\n" + "=" * 70)
    print("PSYCHOLOGIST TOKENIZER READY")
    print("=" * 70)


if __name__ == "__main__":
    main()
