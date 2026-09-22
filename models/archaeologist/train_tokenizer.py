import json
from pathlib import Path
from collections import Counter

# ============================================================
# L.I.M.I.N.A.L. — ARCHAEOLOGIST TOKENIZER TRAINER
# ============================================================

SEED = 42

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent.parent

DATASET_FILE = (
    PROJECT_DIR
    / "dataset"
    / "archaeologist"
    / "archaeologist_v3_train.jsonl"
)

TOKENIZER_DIR = BASE_DIR / "tokenizer"

VOCAB_FILE = TOKENIZER_DIR / "vocab.json"
CONFIG_FILE = TOKENIZER_DIR / "tokenizer_config.json"

VOCAB_SIZE = 8000

SPECIAL_TOKENS = [
    "<PAD>",
    "<UNK>",
    "<BOS>",
    "<EOS>",
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset(path):

    examples = []

    with open(path, "r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            examples.append(
                json.loads(line)
            )

    return examples


# ============================================================
# SIMPLE WORD TOKENIZATION
#
# We intentionally train our own vocabulary.
# No pretrained tokenizer is being used.
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


# ============================================================
# BUILD VOCABULARY
# ============================================================

def build_vocabulary(examples):

    counter = Counter()

    for example in examples:

        text = example["text"]

        tokens = tokenize(text)

        counter.update(tokens)

    # Reserve space for special tokens.
    remaining_size = VOCAB_SIZE - len(SPECIAL_TOKENS)

    most_common = counter.most_common(
        remaining_size
    )

    vocabulary = {}

    # Special tokens first.
    for index, token in enumerate(SPECIAL_TOKENS):

        vocabulary[token] = index

    # Normal vocabulary.
    for token, _ in most_common:

        if token not in vocabulary:

            vocabulary[token] = len(vocabulary)

    return vocabulary, counter


# ============================================================
# SAVE VOCABULARY
# ============================================================

def save_vocabulary(vocabulary):

    TOKENIZER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        VOCAB_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            vocabulary,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# SAVE CONFIG
# ============================================================

def save_config(vocabulary, counter):

    config = {

        "tokenizer_type": "liminal_word_tokenizer",

        "trained_from_scratch": True,

        "vocab_size": len(vocabulary),

        "requested_vocab_size": VOCAB_SIZE,

        "special_tokens": SPECIAL_TOKENS,

        "dataset": str(DATASET_FILE),

        "unique_tokens_in_dataset": len(counter),

        "lowercase": True,

        "max_sequence_length": 128,

        "seed": SEED,
    }

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            config,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# ENCODE FUNCTION
# ============================================================

def encode(text, vocabulary, max_length=128):

    tokens = tokenize(text)

    ids = []

    unk_id = vocabulary["<UNK>"]

    bos_id = vocabulary["<BOS>"]
    eos_id = vocabulary["<EOS>"]

    pad_id = vocabulary["<PAD>"]

    ids.append(bos_id)

    for token in tokens:

        token_id = vocabulary.get(
            token,
            unk_id,
        )

        ids.append(token_id)

    ids.append(eos_id)

    # Truncate.
    ids = ids[:max_length]

    # Padding.
    attention_mask = [1] * len(ids)

    while len(ids) < max_length:

        ids.append(pad_id)
        attention_mask.append(0)

    return ids, attention_mask


# ============================================================
# TEST TOKENIZER
# ============================================================

def test_tokenizer(vocabulary):

    test_sentences = [

        "The report was completed, but nobody explained who approved it.",

        "Maybe someone will handle the issue later.",

        "I was only following instructions.",

        "Sarah submitted the report yesterday.",
    ]

    print()
    print("=" * 70)
    print("TOKENIZER TEST")
    print("=" * 70)

    for sentence in test_sentences:

        tokens = tokenize(sentence)

        ids, mask = encode(
            sentence,
            vocabulary,
            max_length=32,
        )

        print()
        print("TEXT:")
        print(sentence)

        print()
        print("TOKENS:")
        print(tokens)

        print()
        print("IDS:")
        print(ids[:len(tokens) + 2])

        print()
        print("ATTENTION MASK:")
        print(mask[:len(tokens) + 2])

        print("-" * 70)


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("L.I.M.I.N.A.L. — ARCHAEOLOGIST TOKENIZER")
print("=" * 70)

print()
print("Dataset:")
print(DATASET_FILE)

if not DATASET_FILE.exists():

    print()
    print("ERROR: Training dataset not found.")
    print()
    print("Expected:")
    print(DATASET_FILE)

    raise SystemExit(1)


# ------------------------------------------------------------
# Load
# ------------------------------------------------------------

examples = load_dataset(
    DATASET_FILE
)

print()
print(f"Training examples : {len(examples)}")


# ------------------------------------------------------------
# Vocabulary
# ------------------------------------------------------------

vocabulary, counter = build_vocabulary(
    examples
)

print()
print(
    f"Unique tokens found : {len(counter)}"
)

print(
    f"Vocabulary created  : {len(vocabulary)}"
)

print(
    f"Requested vocabulary: {VOCAB_SIZE}"
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

save_vocabulary(
    vocabulary
)

save_config(
    vocabulary,
    counter
)


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------

test_tokenizer(
    vocabulary
)


# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

print()
print("=" * 70)
print("TOKENIZER CREATED")
print("=" * 70)

print()
print("Vocabulary:")
print(VOCAB_FILE)

print()
print("Configuration:")
print(CONFIG_FILE)

print()
print("The Archaeologist tokenizer is trained from scratch.")
print("No pretrained tokenizer was used.")

print()
print("=" * 70)