import json
import sys
import hashlib
import concurrent.futures
from pathlib import Path
import torch


# ============================================================
# PROJECT PATH
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# MODEL IMPORTS
# ============================================================

from models.archaeologist.model import ArchaeologistModel
from models.psychologist.model import PsychologistModel
from models.logician.model import LogicianTransformer
from models.historian.historian import Historian
from models.synthesizer.model import (
    SynthesizerModel,
    text_to_token_ids,
)
from backend.services.azure_explainer import AzureExplainer


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# LABELS
# ============================================================

ARCHAEOLOGIST_LABELS = [
    "NO_OMISSION",
    "HEDGING",
    "MISSING_ACTOR",
    "PASSIVE_CONSTRUCTION",
    "MISSING_COMMITMENT",
    "VAGUE_REFERENCE",
    "RESPONSIBILITY_AVOIDANCE",
]


PSYCHOLOGIST_LABELS = [
    "NO_AFFECT_SIGNAL",
    "AFFECT_GAP",
    "FORCED_POLITENESS",
    "EMOTIONAL_INCONGRUENCE",
    "DISENGAGEMENT_SIGNAL",
    "RESENTMENT_SIGNAL",
    "EMOTIONAL_AVOIDANCE",
]


LOGICIAN_LABELS = [
    "SKIPPED_PREMISE",
    "UNANSWERED_COUNTERARGUMENT",
    "UNSUPPORTED_CONCLUSION",
    "UNSTATED_ASSUMPTION",
    "CONTRADICTION",
    "FALSE_DILEMMA",
]


SYNTHESIZER_LABELS = [
    "NO_SIGNIFICANT_OMISSION",
    "UNSTATED_PREFERENCE",
    "AVOIDING_COMMITMENT",
    "DISTANCING_FROM_RESPONSIBILITY",
    "EMOTIONAL_DISENGAGEMENT",
    "WITHHELD_CONTEXT",
    "UNSUPPORTED_REASONING",
    "AMBIGUOUS_INTENT",
]


# ============================================================
# CHECKPOINT PATHS
# ============================================================

ARCH_CHECKPOINT = (
    ROOT
    / "checkpoints"
    / "archaeologist"
    / "best_model.pt"
)


PSY_CHECKPOINT = (
    ROOT
    / "checkpoints"
    / "psychologist"
    / "best_model.pt"
)


LOG_CHECKPOINT = (
    ROOT
    / "checkpoints"
    / "logician"
    / "best_model.pt"
)


SYN_CHECKPOINT = (
    ROOT
    / "checkpoints"
    / "synthesizer"
    / "best_model.pt"
)


# ============================================================
# TOKENIZERS
# ============================================================

class ArchaeologistTokenizer:

    def __init__(self, vocab_file):

        with open(
            vocab_file,
            "r",
            encoding="utf-8"
        ) as f:

            self.vocab = json.load(f)

        self.pad_id = self.vocab["<PAD>"]
        self.unk_id = self.vocab["<UNK>"]
        self.bos_id = self.vocab["<BOS>"]
        self.eos_id = self.vocab["<EOS>"]

    def encode(
        self,
        text,
        max_length=128
    ):

        tokens = (
            text
            .lower()
            .strip()
            .split()
        )

        token_ids = [self.bos_id]

        for token in tokens:

            token_ids.append(
                self.vocab.get(
                    token,
                    self.unk_id
                )
            )

        token_ids.append(
            self.eos_id
        )

        token_ids = token_ids[:max_length]

        attention_mask = [
            1
        ] * len(token_ids)

        while len(token_ids) < max_length:

            token_ids.append(
                self.pad_id
            )

            attention_mask.append(
                0
            )

        return token_ids, attention_mask


class PsychologistTokenizer:

    def __init__(self, vocab_file):

        import re

        self.re = re

        with open(
            vocab_file,
            "r",
            encoding="utf-8"
        ) as f:

            self.vocab = json.load(f)

        self.pad_id = self.vocab["<PAD>"]
        self.unk_id = self.vocab["<UNK>"]
        self.bos_id = self.vocab["<BOS>"]
        self.eos_id = self.vocab["<EOS>"]

    def tokenize(self, text):

        text = (
            text
            .lower()
            .strip()
        )

        return self.re.findall(
            r"\w+|[^\w\s]",
            text,
            flags=self.re.UNICODE
        )

    def encode(
        self,
        text,
        max_length=128
    ):

        tokens = self.tokenize(
            text
        )

        token_ids = [
            self.vocab.get(
                token,
                self.unk_id
            )
            for token in tokens
        ]

        token_ids = (
            [self.bos_id]
            + token_ids
            + [self.eos_id]
        )

        if len(token_ids) > max_length:

            token_ids = (
                token_ids[:max_length - 1]
                + [self.eos_id]
            )

        padding_length = (
            max_length
            - len(token_ids)
        )

        token_ids += (
            [self.pad_id]
            * padding_length
        )

        return token_ids


class LogicianTokenizer:

    def __init__(self, vocab_file):

        import re

        self.re = re

        with open(
            vocab_file,
            "r",
            encoding="utf-8"
        ) as f:

            self.vocab = json.load(f)

        self.pad_id = self.vocab["<PAD>"]
        self.unk_id = self.vocab["<UNK>"]
        self.bos_id = self.vocab["<BOS>"]
        self.eos_id = self.vocab["<EOS>"]

    def tokenize(self, text):

        return self.re.findall(
            r"[A-Za-z0-9']+",
            text.lower()
        )

    def encode(
        self,
        text,
        max_length=128
    ):

        tokens = self.tokenize(
            text
        )

        ids = [
            self.vocab.get(
                token,
                self.unk_id
            )
            for token in tokens
        ]

        ids = ids[
            :max_length - 2
        ]

        ids = (
            [self.bos_id]
            + ids
            + [self.eos_id]
        )

        attention_mask = [
            1
        ] * len(ids)

        padding_length = (
            max_length
            - len(ids)
        )

        if padding_length > 0:

            ids += (
                [self.pad_id]
                * padding_length
            )

            attention_mask += (
                [0]
                * padding_length
            )

        return ids, attention_mask


# ============================================================
# L.I.M.I.N.A.L. AGENT RUNNER
# ============================================================

class LIMINALAgentRunner:

    def __init__(self):

        print("=" * 70)
        print(
            "L.I.M.I.N.A.L. AGENT INITIALIZATION"
        )
        print("=" * 70)

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

        # ----------------------------------------------------
        # M1
        # ----------------------------------------------------

        self.archaeologist = (
            self._load_archaeologist()
        )

        # ----------------------------------------------------
        # M2
        # ----------------------------------------------------

        self.psychologist = (
            self._load_psychologist()
        )

        # ----------------------------------------------------
        # M3
        # ----------------------------------------------------

        self.logician = (
            self._load_logician()
        )

        # ----------------------------------------------------
        # M4
        # ----------------------------------------------------

        print("\nLoading Historian...")

        self.historian = Historian()

        print(
            "Historian loaded."
        )

        # ----------------------------------------------------
        # M5
        # ----------------------------------------------------

        self.synthesizer = (
            self._load_synthesizer()
        )

        # ----------------------------------------------------
        # Azure GPT-6 Astra explanation layer
        # ----------------------------------------------------

        print("\nLoading Azure GPT-6 Astra...")

        try:

            self.azure_explainer = AzureExplainer()
            self.azure_status = "ready"

            print(
                "GPT-6 Astra explanation layer ready."
            )

        except Exception as exc:

            self.azure_explainer = None
            self.azure_status = f"unavailable: {exc}"

            print(
                f"GPT-6 Astra unavailable: {exc}"
            )

        self._cache = {}

        print("\n" + "=" * 70)

        print(
            "ALL FIVE MODELS READY"
        )

        print("=" * 70)


    # ========================================================
    # LOAD M1
    # ========================================================

    def _load_archaeologist(self):

        print(
            "\nLoading Archaeologist..."
        )

        vocab_file = (
            ROOT
            / "models"
            / "archaeologist"
            / "tokenizer"
            / "vocab.json"
        )

        with open(
            vocab_file,
            "r",
            encoding="utf-8"
        ) as f:

            vocabulary = json.load(f)

        tokenizer = ArchaeologistTokenizer(
            vocab_file
        )

        model = ArchaeologistModel(
            vocab_size=len(vocabulary),
            num_labels=7,
            embedding_dimension=256,
            num_attention_heads=8,
            num_transformer_layers=4,
            feed_forward_dimension=1024,
            max_sequence_length=128,
            dropout=0.1
        )

        checkpoint = torch.load(
            ARCH_CHECKPOINT,
            map_location=DEVICE,
            weights_only=False
        )

        if (
            isinstance(checkpoint, dict)
            and "model_state_dict" in checkpoint
        ):

            model.load_state_dict(
                checkpoint[
                    "model_state_dict"
                ]
            )

        else:

            model.load_state_dict(
                checkpoint
            )

        model = model.to(
            DEVICE
        )

        model.eval()

        print(
            f"Archaeologist loaded "
            f"({len(vocabulary)} vocab)"
        )

        return {
            "model": model,
            "tokenizer": tokenizer
        }


    # ========================================================
    # LOAD M2
    # ========================================================

    def _load_psychologist(self):

        print(
            "\nLoading Psychologist..."
        )

        vocab_file = (
            ROOT
            / "models"
            / "psychologist"
            / "tokenizer"
            / "vocab.json"
        )

        with open(
            vocab_file,
            "r",
            encoding="utf-8"
        ) as f:

            vocabulary = json.load(f)

        checkpoint = torch.load(
            PSY_CHECKPOINT,
            map_location=DEVICE,
            weights_only=False
        )

        model = PsychologistModel(
            vocab_size=checkpoint[
                "vocab_size"
            ],
            num_labels=checkpoint[
                "num_labels"
            ],
            embedding_dimension=checkpoint[
                "embedding_dimension"
            ],
            num_attention_heads=checkpoint[
                "num_attention_heads"
            ],
            num_transformer_layers=checkpoint[
                "num_transformer_layers"
            ],
            feed_forward_dimension=checkpoint[
                "feed_forward_dimension"
            ],
            max_sequence_length=checkpoint[
                "max_sequence_length"
            ],
            dropout=checkpoint[
                "dropout"
            ]
        )

        model.load_state_dict(
            checkpoint[
                "model_state_dict"
            ]
        )

        model = model.to(
            DEVICE
        )

        model.eval()

        tokenizer = PsychologistTokenizer(
            vocab_file
        )

        print(
            f"Psychologist loaded "
            f"({len(vocabulary)} vocab)"
        )

        return {
            "model": model,
            "tokenizer": tokenizer
        }


    # ========================================================
    # LOAD M3
    # ========================================================

    def _load_logician(self):

        print(
            "\nLoading Logician..."
        )

        vocab_file = (
            ROOT
            / "models"
            / "logician"
            / "tokenizer"
            / "vocab.json"
        )

        with open(
            vocab_file,
            "r",
            encoding="utf-8"
        ) as f:

            vocabulary = json.load(f)

        checkpoint = torch.load(
            LOG_CHECKPOINT,
            map_location=DEVICE,
            weights_only=False
        )

        model = LogicianTransformer(
            vocab_size=len(vocabulary),
            num_labels=6,
            embedding_dim=192,
            num_heads=6,
            num_layers=3,
            feedforward_dim=768,
            max_seq_len=128,
            dropout=0.30
        )

        if (
            isinstance(checkpoint, dict)
            and "model_state_dict" in checkpoint
        ):

            model.load_state_dict(
                checkpoint[
                    "model_state_dict"
                ]
            )

        else:

            model.load_state_dict(
                checkpoint
            )

        model = model.to(
            DEVICE
        )

        model.eval()

        tokenizer = LogicianTokenizer(
            vocab_file
        )

        print(
            f"Logician loaded "
            f"({len(vocabulary)} vocab)"
        )

        return {
            "model": model,
            "tokenizer": tokenizer
        }


    # ========================================================
    # LOAD M5
    # ========================================================

    def _load_synthesizer(self):

        print(
            "\nLoading Synthesizer..."
        )

        # PyTorch 2.6+ defaults to weights_only=True.
        # This checkpoint was created by our own training
        # pipeline and contains metadata/NumPy objects, so
        # explicitly allow the complete trusted checkpoint.
        checkpoint = torch.load(
            SYN_CHECKPOINT,
            map_location=DEVICE,
            weights_only=False
        )

        metadata = checkpoint.get(
            "metadata",
            checkpoint,
        )

        model = SynthesizerModel(
            input_dim=metadata.get(
                "input_dim",
                checkpoint.get("input_dim", 25),
            ),
            hidden_dim=metadata.get(
                "hidden_dim",
                checkpoint.get("hidden_dim", 96),
            ),
            num_classes=metadata.get(
                "num_classes",
                checkpoint.get("num_classes", 8),
            ),
            dropout=metadata.get(
                "dropout",
                checkpoint.get("dropout", 0.20),
            ),
        )

        try:

            model.load_state_dict(
                checkpoint[
                    "model_state_dict"
                ]
            )

        except RuntimeError as exc:

            raise RuntimeError(
                "The M5 checkpoint is incompatible with the "
                "current SynthesizerModel. Train the new "
                "text-aware M5 model first with: "
                "python .\\models\\synthesizer\\train.py"
            ) from exc

        model = model.to(
            DEVICE
        )

        model.eval()

        print(
            f"Synthesizer loaded "
            f"({sum(p.numel() for p in model.parameters()):,} parameters)"
        )

        return model


    # ========================================================
    # M1 INFERENCE
    # ========================================================

    def _get_archaeologist_probabilities(
        self,
        text
    ):

        model = self.archaeologist[
            "model"
        ]

        tokenizer = self.archaeologist[
            "tokenizer"
        ]

        input_ids, attention_mask = (
            tokenizer.encode(text)
        )

        input_ids = torch.tensor(
            [input_ids],
            dtype=torch.long,
            device=DEVICE
        )

        attention_mask = torch.tensor(
            [attention_mask],
            dtype=torch.long,
            device=DEVICE
        )

        with torch.no_grad():

            logits = model(
                input_ids,
                attention_mask
            )

            probabilities = torch.sigmoid(
                logits
            )[0]

        return [
            float(
                probabilities[i].item()
            )
            for i in range(
                len(ARCHAEOLOGIST_LABELS)
            )
        ]


    def run_archaeologist(
        self,
        text
    ):

        probabilities = (
            self._get_archaeologist_probabilities(
                text
            )
        )

        findings = []

        for label, probability in zip(
            ARCHAEOLOGIST_LABELS,
            probabilities
        ):

            if probability >= 0.5:

                findings.append({
                    "label": label,
                    "probability": round(
                        probability,
                        4
                    )
                })

        return {
            "agent": "archaeologist",
            "findings": findings
        }


    # ========================================================
    # M2 INFERENCE
    # ========================================================

    def _get_psychologist_probabilities(
        self,
        text
    ):

        model = self.psychologist[
            "model"
        ]

        tokenizer = self.psychologist[
            "tokenizer"
        ]

        input_ids = tokenizer.encode(
            text
        )

        input_ids = torch.tensor(
            [input_ids],
            dtype=torch.long,
            device=DEVICE
        )

        with torch.no_grad():

            logits = model(
                input_ids
            )

            probabilities = torch.sigmoid(
                logits
            )[0]

        return [
            float(
                probabilities[i].item()
            )
            for i in range(
                len(PSYCHOLOGIST_LABELS)
            )
        ]


    def run_psychologist(
        self,
        text
    ):

        probabilities = (
            self._get_psychologist_probabilities(
                text
            )
        )

        findings = []

        for label, probability in zip(
            PSYCHOLOGIST_LABELS,
            probabilities
        ):

            if probability >= 0.5:

                findings.append({
                    "label": label,
                    "probability": round(
                        probability,
                        4
                    )
                })

        return {
            "agent": "psychologist",
            "findings": findings
        }


    # ========================================================
    # M3 INFERENCE
    # ========================================================

    def _get_logician_probabilities(
        self,
        text
    ):

        model = self.logician[
            "model"
        ]

        tokenizer = self.logician[
            "tokenizer"
        ]

        input_ids, attention_mask = (
            tokenizer.encode(text)
        )

        input_ids = torch.tensor(
            [input_ids],
            dtype=torch.long,
            device=DEVICE
        )

        attention_mask = torch.tensor(
            [attention_mask],
            dtype=torch.long,
            device=DEVICE
        )

        with torch.no_grad():

            logits = model(
                input_ids,
                attention_mask
            )

            probabilities = torch.sigmoid(
                logits
            )[0]

        return [
            float(
                probabilities[i].item()
            )
            for i in range(
                len(LOGICIAN_LABELS)
            )
        ]


    def run_logician(
        self,
        text
    ):

        probabilities = (
            self._get_logician_probabilities(
                text
            )
        )

        findings = []

        for label, probability in zip(
            LOGICIAN_LABELS,
            probabilities
        ):

            if probability >= 0.5:

                findings.append({
                    "label": label,
                    "probability": round(
                        probability,
                        4
                    )
                })

        return {
            "agent": "logician",
            "findings": findings
        }


    # ========================================================
    # M4 INFERENCE
    # ========================================================

    def run_historian(
        self,
        text
    ):

        return self.historian.analyze(
            text,
            top_k=5
        )


    # ========================================================
    # M4 → FEATURE VECTOR
    # ========================================================

    def _get_historian_features(
        self,
        historian_result
    ):
        """
        Convert Historian output into the exact five similarity
        features expected by the trained M5 Synthesizer.

        Historian.analyze() currently returns a list of evidence
        records, but this also supports a dictionary containing
        an "evidence" list for forward compatibility.
        """

        # --------------------------------------------------------
        # Normalize Historian output
        # --------------------------------------------------------

        if isinstance(historian_result, list):

            evidence = historian_result

        elif isinstance(historian_result, dict):

            evidence = historian_result.get(
                "evidence",
                []
            )

        else:

            evidence = []

        # --------------------------------------------------------
        # Extract similarity scores
        # --------------------------------------------------------

        scores = []

        for item in evidence:

            if not isinstance(item, dict):
                continue

            # M4's trained/expected feature is similarity.
            # Do NOT substitute raw FAISS distance here because
            # distance has the opposite meaning.
            score = item.get(
                "similarity",
                item.get(
                    "score",
                    0.0
                )
            )

            try:

                score = float(score)

            except (
                TypeError,
                ValueError
            ):

                score = 0.0

            scores.append(score)

        # --------------------------------------------------------
        # Highest-similarity evidence first
        # --------------------------------------------------------

        scores.sort(
            reverse=True
        )

        # M5 was trained with exactly five M4 features.
        scores = scores[:5]

        while len(scores) < 5:

            scores.append(0.0)

        return scores


    # ========================================================
    # BUILD M5 FEATURE VECTOR
    # ========================================================

    def _build_synthesizer_features(
        self,
        archaeologist_probabilities,
        psychologist_probabilities,
        logician_probabilities,
        historian_result
    ):

        historian_features = (
            self._get_historian_features(
                historian_result
            )
        )

        features = (
            archaeologist_probabilities
            + psychologist_probabilities
            + logician_probabilities
            + historian_features
        )

        if len(features) != 25:

            raise RuntimeError(
                "M5 feature vector must contain "
                f"25 values, got {len(features)}."
            )

        return features


    # ========================================================
    # M5 INFERENCE
    # ========================================================

    def run_synthesizer(
        self,
        features,
        text=None,
    ):

        feature_tensor = torch.tensor(
            [features],
            dtype=torch.float32,
            device=DEVICE,
        )

        # ----------------------------------------------------
        # M5 text input
        # ----------------------------------------------------

        token_ids = None

        if text is not None:

            token_ids = [
                text_to_token_ids(text)
            ]

        # ----------------------------------------------------
        # M5 inference
        # ----------------------------------------------------

        with torch.no_grad():

            synth_output = self.synthesizer(
                feature_tensor,
                token_ids,
            )

            if not isinstance(
                synth_output,
                dict
            ):

                raise RuntimeError(
                    "SynthesizerModel must return a dictionary "
                    "containing 'subtext_logits'."
                )

            if "subtext_logits" not in synth_output:

                raise RuntimeError(
                    "SynthesizerModel output is missing "
                    "'subtext_logits'. "
                    f"Available keys: {list(synth_output.keys())}"
                )

            logits = synth_output[
                "subtext_logits"
            ]

            if not torch.is_tensor(
                logits
            ):

                raise RuntimeError(
                    "Synthesizer 'subtext_logits' "
                    "must be a tensor."
                )

            if logits.dim() == 1:

                logits = logits.unsqueeze(0)

            probabilities = torch.softmax(
                logits,
                dim=-1,
            )

            sample_probabilities = probabilities[0]

        predicted_id = int(
            torch.argmax(
                sample_probabilities,
                dim=-1,
            ).item()
        )

        if predicted_id >= len(
            SYNTHESIZER_LABELS
        ):

            raise RuntimeError(
                "Synthesizer predicted class index "
                f"{predicted_id}, but only "
                f"{len(SYNTHESIZER_LABELS)} labels are defined."
            )

        predicted_label = (
            SYNTHESIZER_LABELS[
                predicted_id
            ]
        )

        confidence = float(
            sample_probabilities[
                predicted_id
            ].item()
        )

        class_probabilities = {}

        probability_values = (
            sample_probabilities
            .detach()
            .cpu()
            .tolist()
        )

        if len(probability_values) != len(
            SYNTHESIZER_LABELS
        ):

            raise RuntimeError(
                "Synthesizer output class count does not match "
                f"SYNTHESIZER_LABELS: got "
                f"{len(probability_values)}, expected "
                f"{len(SYNTHESIZER_LABELS)}."
            )

        for label, probability in zip(
            SYNTHESIZER_LABELS,
            probability_values,
        ):

            class_probabilities[
                label
            ] = round(
                float(probability),
                4,
            )

        result = {
            "agent": "synthesizer",
            "prediction": predicted_label,
            "confidence": round(
                confidence,
                4,
            ),
            "class_probabilities":
                class_probabilities,
        }

        if "confidence" in synth_output:

            model_confidence = (
                synth_output["confidence"]
            )

            if torch.is_tensor(
                model_confidence
            ):

                if model_confidence.numel() > 0:

                    result["model_confidence"] = round(
                        float(
                            model_confidence
                            .reshape(-1)[0]
                            .item()
                        ),
                        4,
                    )

        return result


    # ========================================================
    # DOSSIER RENDERING
    # ========================================================

    def _render_dossier(
        self,
        text,
        synthesizer,
        archaeologist,
        psychologist,
        logician,
        historian
    ):

        label = synthesizer[
            "prediction"
        ]

        confidence = synthesizer[
            "confidence"
        ]

        # Normalize Historian output for dossier rendering.
        if isinstance(historian, dict):

            evidence = historian.get(
                "evidence",
                []
            )

        elif isinstance(historian, list):

            evidence = historian

        else:

            evidence = []

        subtext_map = {

            "NO_SIGNIFICANT_OMISSION":
                (
                    "No strong omission pattern "
                    "was detected across the "
                    "available communication signals."
                ),

            "UNSTATED_PREFERENCE":
                (
                    "The message may leave the "
                    "speaker's actual preference "
                    "or position unstated."
                ),

            "AVOIDING_COMMITMENT":
                (
                    "The wording may reduce or "
                    "avoid making a clear commitment."
                ),

            "DISTANCING_FROM_RESPONSIBILITY":
                (
                    "The wording may reduce clarity "
                    "about who owns the decision, "
                    "action, or responsibility."
                ),

            "EMOTIONAL_DISENGAGEMENT":
                (
                    "The message contains signals "
                    "consistent with reduced emotional "
                    "engagement, although this cannot "
                    "establish the speaker's internal state."
                ),

            "WITHHELD_CONTEXT":
                (
                    "Important contextual information "
                    "may be left unspecified or unclear."
                ),

            "UNSUPPORTED_REASONING":
                (
                    "The message may rely on an "
                    "unstated premise or reasoning "
                    "step that is not explicitly provided."
                ),

            "AMBIGUOUS_INTENT":
                (
                    "The wording allows multiple "
                    "reasonable interpretations of "
                    "the speaker's communicative intent."
                )
        }

        missing_map = {

            "NO_SIGNIFICANT_OMISSION": [],

            "UNSTATED_PREFERENCE": [
                "Explicit preference",
                "Clear personal position"
            ],

            "AVOIDING_COMMITMENT": [
                "Specific commitment",
                "Concrete next step",
                "Clear decision"
            ],

            "DISTANCING_FROM_RESPONSIBILITY": [
                "Decision owner",
                "Accountability",
                "Specific actor"
            ],

            "EMOTIONAL_DISENGAGEMENT": [
                "Explicit emotional signal",
                "Direct engagement",
                "Reason for the emotional gap"
            ],

            "WITHHELD_CONTEXT": [
                "Relevant context",
                "Specific actors",
                "Supporting details"
            ],

            "UNSUPPORTED_REASONING": [
                "Supporting premise",
                "Evidence",
                "Reasoning step"
            ],

            "AMBIGUOUS_INTENT": [
                "Explicit intent",
                "Clear preference",
                "Additional context"
            ]
        }

        return {

            "surface_statement": text,

            "possible_subtext":
                subtext_map.get(
                    label,
                    "No interpretation available."
                ),

            "primary_pattern": label,

            "confidence": round(
                confidence * 100,
                2
            ),

            "strategically_missing": (
                missing_map.get(
                    label,
                    []
                )
            ),

            "agent_findings": {

                "archaeologist":
                    archaeologist["findings"],

                "psychologist":
                    psychologist["findings"],

                "logician":
                    logician["findings"]
            },

            "evidence":
                evidence,

            "responsible_ai_note": (
                "The result describes "
                "observable communication patterns "
                "and possible interpretations. "
                "It does not establish a person's "
                "private thoughts, emotions, intentions, "
                "or motives as facts."
            )
        }


    # ========================================================
    # COMPLETE ANALYSIS
    # ========================================================

    # ========================================================
    # CONCURRENT AGENT EXECUTORS
    # ========================================================

    def _execute_m1(self, text):
        probs = self._get_archaeologist_probabilities(text)
        findings = [
            {"label": label, "probability": round(p, 4)}
            for label, p in zip(ARCHAEOLOGIST_LABELS, probs)
            if p >= 0.5
        ]
        return probs, {"agent": "archaeologist", "findings": findings}

    def _execute_m2(self, text):
        probs = self._get_psychologist_probabilities(text)
        findings = [
            {"label": label, "probability": round(p, 4)}
            for label, p in zip(PSYCHOLOGIST_LABELS, probs)
            if p >= 0.5
        ]
        return probs, {"agent": "psychologist", "findings": findings}

    def _execute_m3(self, text):
        probs = self._get_logician_probabilities(text)
        findings = [
            {"label": label, "probability": round(p, 4)}
            for label, p in zip(LOGICIAN_LABELS, probs)
            if p >= 0.5
        ]
        return probs, {"agent": "logician", "findings": findings}

    def _execute_m4(self, text):
        return self.run_historian(text)

    # ========================================================
    # COMPLETE ANALYSIS (PARALLELIZED + CACHED)
    # ========================================================

    def analyze(
        self,
        text,
        include_azure=True,
    ):
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        text = text.strip()
        cache_key = f"{hashlib.sha256(text.encode('utf-8')).hexdigest()}_{include_azure}"
        if cache_key in self._cache:
            print("[CACHE] Returning cached analysis")
            return self._cache[cache_key]

        print("\n" + "=" * 70)
        print("L.I.M.I.N.A.L. MULTI-AGENT PARALLEL ANALYSIS")
        print("=" * 70)
        print(f"\nINPUT:\n{text}")

        # Run M1-M4 concurrently in thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            f_m1 = executor.submit(self._execute_m1, text)
            f_m2 = executor.submit(self._execute_m2, text)
            f_m3 = executor.submit(self._execute_m3, text)
            f_m4 = executor.submit(self._execute_m4, text)

            archaeologist_probabilities, archaeologist = f_m1.result()
            psychologist_probabilities, psychologist = f_m2.result()
            logician_probabilities, logician = f_m3.result()
            historian = f_m4.result()

        print(f"M1-M4 parallel execution complete.")

        # Build M5 input features (25-dim)
        features = self._build_synthesizer_features(
            archaeologist_probabilities,
            psychologist_probabilities,
            logician_probabilities,
            historian,
        )

        # M5 Synthesizer Fusion
        synthesizer = self.run_synthesizer(features, text)
        print(f"Synthesizer: {synthesizer['prediction']} ({synthesizer['confidence']:.4f})")

        # Dossier
        dossier = self._render_dossier(
            text,
            synthesizer,
            archaeologist,
            psychologist,
            logician,
            historian,
        )

        # Azure GPT-6 Astra explanation
        azure_explanation = None
        if include_azure and self.azure_explainer is not None:
            print("\n[AZURE] GPT-6 Astra explanation...")
            try:
                azure_explanation = self.azure_explainer.explain(dossier)
                print("[AZURE] GPT-6 Astra explanation complete.")
            except Exception as exc:
                print(f"[AZURE] Explanation error: {exc}")
        elif not include_azure:
            azure_explanation = "Azure explanation skipped for ultra-fast local inference."

        dossier["azure_explanation"] = azure_explanation

        result = {
            "input": text,
            "agents": {
                "archaeologist": archaeologist,
                "psychologist": psychologist,
                "logician": logician,
                "historian": historian,
                "synthesizer": synthesizer,
            },
            "synthesizer_features": features,
            "azure": {
                "enabled": self.azure_explainer is not None and include_azure,
                "status": self.azure_status if include_azure else "skipped",
            },
            "dossier": dossier,
        }

        if len(self._cache) > 100:
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = result

        return result

    # ========================================================
    # REAL-TIME STREAMING ANALYSIS GENERATOR
    # ========================================================

    def analyze_stream(
        self,
        text,
        include_azure=True,
    ):
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        text = text.strip()
        yield {"event": "start", "input": text}

        # Track completed tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_map = {
                executor.submit(self._execute_m1, text): "archaeologist",
                executor.submit(self._execute_m2, text): "psychologist",
                executor.submit(self._execute_m3, text): "logician",
                executor.submit(self._execute_m4, text): "historian",
            }

            archaeologist_probabilities = None
            archaeologist = None
            psychologist_probabilities = None
            psychologist = None
            logician_probabilities = None
            logician = None
            historian = None

            for future in concurrent.futures.as_completed(future_map):
                agent_name = future_map[future]
                res = future.result()

                if agent_name == "archaeologist":
                    archaeologist_probabilities, archaeologist = res
                    yield {"event": "agent_complete", "agent": "archaeologist", "data": archaeologist}
                elif agent_name == "psychologist":
                    psychologist_probabilities, psychologist = res
                    yield {"event": "agent_complete", "agent": "psychologist", "data": psychologist}
                elif agent_name == "logician":
                    logician_probabilities, logician = res
                    yield {"event": "agent_complete", "agent": "logician", "data": logician}
                elif agent_name == "historian":
                    historian = res
                    yield {"event": "agent_complete", "agent": "historian", "data": historian}

        # Build M5 features
        features = self._build_synthesizer_features(
            archaeologist_probabilities,
            psychologist_probabilities,
            logician_probabilities,
            historian,
        )

        # Run M5
        synthesizer = self.run_synthesizer(features, text)
        yield {"event": "agent_complete", "agent": "synthesizer", "data": synthesizer}

        # Render Dossier
        dossier = self._render_dossier(
            text,
            synthesizer,
            archaeologist,
            psychologist,
            logician,
            historian,
        )

        azure_explanation = None
        if include_azure and self.azure_explainer is not None:
            yield {"event": "azure_start"}
            try:
                azure_explanation = self.azure_explainer.explain(dossier)
                yield {"event": "azure_complete", "explanation": azure_explanation}
            except Exception as exc:
                azure_explanation = f"Azure unavailable: {exc}"
                yield {"event": "azure_complete", "explanation": azure_explanation}
        elif not include_azure:
            azure_explanation = "Azure explanation skipped for ultra-fast local inference."
            yield {"event": "azure_complete", "explanation": azure_explanation}

        dossier["azure_explanation"] = azure_explanation

        result = {
            "input": text,
            "agents": {
                "archaeologist": archaeologist,
                "psychologist": psychologist,
                "logician": logician,
                "historian": historian,
                "synthesizer": synthesizer,
            },
            "synthesizer_features": features,
            "azure": {
                "enabled": self.azure_explainer is not None and include_azure,
                "status": self.azure_status if include_azure else "skipped",
            },
            "dossier": dossier,
        }

        yield {"event": "done", "result": result}


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    runner = (
        LIMINALAgentRunner()
    )

    test_text = (
        "I'm fine with whatever you decide. "
        "The current plan should probably work."
    )

    result = runner.analyze(
        test_text
    )

    print("\n")
    print("=" * 70)

    print(
        "SUBTEXT DOSSIER"
    )

    print("=" * 70)

    print(
        json.dumps(
            result["dossier"],
            indent=2,
            ensure_ascii=False
        )
    )