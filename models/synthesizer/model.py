import hashlib
import re

import torch
import torch.nn as nn


# ============================================================
# LABELS
# ============================================================

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
# TEXT HASHING
# ============================================================

TEXT_BUCKETS = 256
MAX_TEXT_TOKENS = 64


def tokenize_text(text):
    """
    Small deterministic tokenizer.

    No pretrained tokenizer.
    No external vocabulary.

    This keeps inference completely reproducible.
    """

    text = str(text).lower()

    tokens = re.findall(
        r"[a-z0-9]+(?:'[a-z]+)?",
        text,
    )

    if not tokens:
        return ["<empty>"]

    return tokens[:MAX_TEXT_TOKENS]


def token_to_bucket(token):
    """
    Deterministic SHA-256 hashing.

    Python's built-in hash() is intentionally randomized
    between processes, so it must NOT be used here.
    """

    digest = hashlib.sha256(
        token.encode("utf-8")
    ).digest()

    value = int.from_bytes(
        digest[:4],
        byteorder="little",
        signed=False,
    )

    return value % TEXT_BUCKETS


def text_to_token_ids(text):
    tokens = tokenize_text(text)

    return [
        token_to_bucket(token)
        for token in tokens
    ]


# ============================================================
# M5 MODEL
# ============================================================

class SynthesizerModel(nn.Module):

    def __init__(
        self,
        input_dim=25,
        hidden_dim=96,
        num_classes=8,
        dropout=0.20,
    ):

        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        self.dropout_rate = dropout

        # ----------------------------------------------------
        # Text encoder
        #
        # Randomly initialized.
        # No pretrained weights.
        # ----------------------------------------------------

        self.text_embedding = nn.Embedding(
            num_embeddings=TEXT_BUCKETS,
            embedding_dim=64,
        )

        self.text_encoder = nn.Sequential(
            nn.Linear(64, 64),
            nn.GELU(),
            nn.LayerNorm(64),
            nn.Dropout(dropout),
            nn.Linear(64, 48),
            nn.GELU(),
        )

        # ----------------------------------------------------
        # Production M1-M4 feature encoder
        # ----------------------------------------------------

        self.feature_encoder = nn.Sequential(
            nn.LayerNorm(input_dim),
            nn.Linear(
                input_dim,
                hidden_dim,
            ),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(
                hidden_dim,
                64,
            ),
            nn.GELU(),
        )

        # ----------------------------------------------------
        # Fusion
        #
        # 64 agent features
        # +
        # 48 text features
        # =
        # 112 dimensions
        # ----------------------------------------------------

        self.fusion = nn.Sequential(
            nn.LayerNorm(112),

            nn.Linear(
                112,
                96,
            ),

            nn.GELU(),

            nn.Dropout(dropout),

            nn.Linear(
                96,
                64,
            ),

            nn.GELU(),

            nn.Dropout(dropout),
        )

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        self.classifier = nn.Linear(
            64,
            num_classes,
        )

        # ----------------------------------------------------
        # Confidence head
        # ----------------------------------------------------

        self.confidence_head = nn.Sequential(
            nn.Linear(
                64,
                32,
            ),

            nn.GELU(),

            nn.Linear(
                32,
                1,
            ),

            nn.Sigmoid(),
        )

        # ----------------------------------------------------
        # Explicit random initialization
        # ----------------------------------------------------

        self._initialize_weights()

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def _initialize_weights(self):

        for module in self.modules():

            if isinstance(
                module,
                nn.Linear,
            ):

                nn.init.xavier_uniform_(
                    module.weight
                )

                if module.bias is not None:

                    nn.init.zeros_(
                        module.bias
                    )

            elif isinstance(
                module,
                nn.Embedding,
            ):

                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=0.02,
                )

    # ========================================================
    # TEXT ENCODING
    # ========================================================

    def encode_text_ids(
        self,
        token_ids,
        device=None,
    ):
        """
        token_ids:
            list[list[int]]
        """

        if device is None:

            device = (
                self.text_embedding.weight.device
            )

        batch_size = len(token_ids)

        max_length = max(
            len(x)
            for x in token_ids
        )

        ids = torch.zeros(
            (
                batch_size,
                max_length,
            ),
            dtype=torch.long,
            device=device,
        )

        mask = torch.zeros(
            (
                batch_size,
                max_length,
            ),
            dtype=torch.float32,
            device=device,
        )

        for i, sequence in enumerate(
            token_ids
        ):

            if not sequence:

                continue

            length = min(
                len(sequence),
                max_length,
            )

            ids[
                i,
                :length
            ] = torch.tensor(
                sequence[:length],
                dtype=torch.long,
                device=device,
            )

            mask[
                i,
                :length
            ] = 1.0

        embeddings = self.text_embedding(
            ids
        )

        mask = mask.unsqueeze(-1)

        summed = (
            embeddings * mask
        ).sum(
            dim=1
        )

        counts = mask.sum(
            dim=1
        ).clamp_min(
            1.0
        )

        pooled = (
            summed
            / counts
        )

        return self.text_encoder(
            pooled
        )

    # ========================================================
    # FORWARD
    # ========================================================

    def forward(
        self,
        features,
        token_ids=None,
    ):

        # ----------------------------------------------------
        # M1-M4 representation
        # ----------------------------------------------------

        feature_representation = (
            self.feature_encoder(
                features
            )
        )

        # ----------------------------------------------------
        # Text representation
        # ----------------------------------------------------

        if token_ids is None:

            # Backward-safe zero text representation.
            #
            # This keeps the model usable if an older caller
            # only provides the 25 numerical features.

            text_representation = torch.zeros(
                (
                    features.shape[0],
                    48,
                ),
                dtype=features.dtype,
                device=features.device,
            )

        else:

            text_representation = (
                self.encode_text_ids(
                    token_ids,
                    device=features.device,
                )
            )

        # ----------------------------------------------------
        # Fusion
        # ----------------------------------------------------

        fused = torch.cat(
            [
                feature_representation,
                text_representation,
            ],
            dim=1,
        )

        fused = self.fusion(
            fused
        )

        # ----------------------------------------------------
        # Outputs
        # ----------------------------------------------------

        logits = self.classifier(
            fused
        )

        confidence = self.confidence_head(
            fused
        ).squeeze(-1)

        return {
            "subtext_logits": logits,
            "confidence": confidence,
        }


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    model = SynthesizerModel()

    features = torch.randn(
        2,
        25,
    )

    texts = [
        text_to_token_ids(
            "Nobody complained, therefore everyone must be satisfied."
        ),

        text_to_token_ids(
            "There are circumstances I have not mentioned yet."
        ),
    ]

    output = model(
        features,
        texts,
    )

    print(
        "Logits:",
        output["subtext_logits"].shape,
    )

    print(
        "Confidence:",
        output["confidence"].shape,
    )

    total_parameters = sum(
        p.numel()
        for p in model.parameters()
    )

    print(
        "Parameters:",
        f"{total_parameters:,}",
    )