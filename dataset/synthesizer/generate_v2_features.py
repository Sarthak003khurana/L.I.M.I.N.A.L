import sys
import json
from pathlib import Path

# ------------------------------------------------------------
# Project root
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------

from backend.services.agent_runner import LIMINALAgentRunner


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

INPUT_FILE = (
    ROOT
    / "dataset"
    / "synthesizer_v2"
    / "new_contrastive_examples.jsonl"
)

OUTPUT_FILE = (
    ROOT
    / "dataset"
    / "synthesizer_v2"
    / "new_contrastive_with_features.jsonl"
)


# ------------------------------------------------------------
# Load examples
# ------------------------------------------------------------

examples = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if line:
            examples.append(json.loads(line))


print("Loaded new examples:", len(examples))


# ------------------------------------------------------------
# Load production agents
# ------------------------------------------------------------

print("\nLoading L.I.M.I.N.A.L. agents...")

runner = LIMINALAgentRunner()

print("✓ Agents loaded")


# ------------------------------------------------------------
# Generate production features
# ------------------------------------------------------------

output = []

for i, example in enumerate(examples, start=1):

    text = example["text"]

    print(
        f"[{i}/{len(examples)}] "
        f"{example['label']} | {text}"
    )

    # --------------------------------------------------------
    # M1
    # --------------------------------------------------------

    m1_probs = runner._get_archaeologist_probabilities(text)

    # --------------------------------------------------------
    # M2
    # --------------------------------------------------------

    m2_probs = runner._get_psychologist_probabilities(text)

    # --------------------------------------------------------
    # M3
    # --------------------------------------------------------

    m3_probs = runner._get_logician_probabilities(text)

    # --------------------------------------------------------
    # M4
    # --------------------------------------------------------

    historian_result = runner.run_historian(text)

    m4_features = runner._get_historian_features(
        historian_result
    )

    # --------------------------------------------------------
    # Combine exactly like production M5
    # --------------------------------------------------------

    features = runner._build_synthesizer_features(
        m1_probs,
        m2_probs,
        m3_probs,
        m4_features,
    )

    features = [float(x) for x in features]

    if len(features) != 25:
        raise RuntimeError(
            f"Expected 25 features, got {len(features)} "
            f"for text: {text}"
        )

    # --------------------------------------------------------
    # Build record
    # --------------------------------------------------------

    record = {
        "text": text,
        "family": f"v2_contrastive_{i:04d}",
        "variant_id": 0,
        "difficulty": "hard",
        "source_type": "targeted_contrastive_v2",
        "features": features,
        "label": example["label"],
    }

    output.append(record)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    for record in output:
        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )


# ------------------------------------------------------------
# Verify
# ------------------------------------------------------------

print("\n========================================")
print("FEATURE GENERATION COMPLETE")
print("========================================")

print("Examples:", len(output))
print("Feature size:", len(output[0]["features"]))

print("\nOutput:")
print(OUTPUT_FILE)

print("\nFirst example:")
print(json.dumps(
    output[0],
    indent=2,
    ensure_ascii=False
))

print("\n✓ Existing train/validation/test datasets were NOT modified.")