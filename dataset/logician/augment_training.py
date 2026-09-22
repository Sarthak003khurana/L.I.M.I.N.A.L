import json
from pathlib import Path

base = Path("dataset/logician/logician_v3/train.jsonl")
boundary = Path("dataset/logician/logician_boundary_seeds.jsonl")
output = Path("dataset/logician/logician_v3/train_augmented.jsonl")

def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]

train = load(base)
boundary_rows = load(boundary)

# Add unique family IDs to boundary examples.
# These examples are training-only and will never enter val/test.
for i, row in enumerate(boundary_rows, 1):
    row["family_id"] = f"boundary_{i:03d}"

combined = train + boundary_rows

# Remove exact duplicate texts while preserving order.
seen = set()
clean = []

for row in combined:
    text = row["text"].strip()
    if text not in seen:
        seen.add(text)
        row["text"] = text
        clean.append(row)

with open(output, "w", encoding="utf-8") as f:
    for row in clean:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print("Original training examples:", len(train))
print("Boundary examples:", len(boundary_rows))
print("Final augmented training examples:", len(clean))
print("Duplicates removed:", len(combined) - len(clean))
print("Validation untouched:", base.parent / "val.jsonl")
print("Test untouched:", base.parent / "test.jsonl")
print("Saved:", output)
