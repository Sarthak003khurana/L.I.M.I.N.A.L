import math
from pathlib import Path

import torch
import torch.nn as nn


# ============================================================
# L.I.M.I.N.A.L. — ARCHAEOLOGIST MODEL
# ============================================================
#
# A Transformer encoder trained from RANDOM INITIALIZATION.
#
# Task:
# Multi-label classification of linguistic omissions.
#
# Labels:
#   0 - NO_OMISSION
#   1 - HEDGING
#   2 - MISSING_ACTOR
#   3 - PASSIVE_CONSTRUCTION
#   4 - MISSING_COMMITMENT
#   5 - VAGUE_REFERENCE
#   6 - RESPONSIBILITY_AVOIDANCE
#
# No pretrained model weights are used.
# No pretrained Transformer is used.
# ============================================================


class PositionalEncoding(nn.Module):
    """
    Learnable positional embeddings.

    Each token receives:
        token embedding + position embedding
    """

    def __init__(
        self,
        max_sequence_length,
        embedding_dimension,
    ):
        super().__init__()

        self.position_embedding = nn.Embedding(
            max_sequence_length,
            embedding_dimension,
        )

    def forward(self, x):

        # x shape:
        # [batch_size, sequence_length, embedding_dimension]

        batch_size, sequence_length, _ = x.shape

        positions = torch.arange(
            sequence_length,
            device=x.device,
        )

        positions = positions.unsqueeze(0).expand(
            batch_size,
            sequence_length,
        )

        position_vectors = self.position_embedding(
            positions
        )

        return x + position_vectors


class ArchaeologistModel(nn.Module):
    """
    L.I.M.I.N.A.L. Archaeologist.

    Randomly initialized Transformer encoder
    followed by a multi-label classification head.
    """

    def __init__(
        self,
        vocab_size,
        num_labels=7,
        embedding_dimension=256,
        num_attention_heads=8,
        num_transformer_layers=4,
        feed_forward_dimension=1024,
        max_sequence_length=128,
        dropout=0.1,
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.num_labels = num_labels
        self.embedding_dimension = embedding_dimension
        self.max_sequence_length = max_sequence_length

        # ----------------------------------------------------
        # Token embedding
        # ----------------------------------------------------

        self.token_embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dimension,
        )

        # ----------------------------------------------------
        # Position embedding
        # ----------------------------------------------------

        self.position_encoding = PositionalEncoding(
            max_sequence_length=max_sequence_length,
            embedding_dimension=embedding_dimension,
        )

        # ----------------------------------------------------
        # Transformer encoder
        # ----------------------------------------------------

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dimension,
            nhead=num_attention_heads,
            dim_feedforward=feed_forward_dimension,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=False,
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer=encoder_layer,
            num_layers=num_transformer_layers,
        )

        # ----------------------------------------------------
        # Final normalization
        # ----------------------------------------------------

        self.final_norm = nn.LayerNorm(
            embedding_dimension
        )

        # ----------------------------------------------------
        # Classification head
        # ----------------------------------------------------

        self.classifier = nn.Sequential(

            nn.Linear(
                embedding_dimension,
                embedding_dimension,
            ),

            nn.GELU(),

            nn.Dropout(dropout),

            nn.Linear(
                embedding_dimension,
                num_labels,
            ),
        )

        # ----------------------------------------------------
        # Initialize weights
        #
        # PyTorch already initializes these randomly,
        # but we explicitly initialize them here so the
        # from-scratch design is clear and reproducible.
        # ----------------------------------------------------

        self._initialize_weights()


    def _initialize_weights(self):

        for module in self.modules():

            if isinstance(module, nn.Linear):

                nn.init.xavier_uniform_(
                    module.weight
                )

                if module.bias is not None:

                    nn.init.zeros_(
                        module.bias
                    )

            elif isinstance(module, nn.Embedding):

                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=0.02,
                )

            elif isinstance(module, nn.LayerNorm):

                nn.init.ones_(
                    module.weight
                )

                nn.init.zeros_(
                    module.bias
                )


    def masked_mean_pooling(
        self,
        hidden_states,
        attention_mask,
    ):
        """
        Mean-pool only real tokens.

        hidden_states:
            [batch, sequence, hidden]

        attention_mask:
            [batch, sequence]

        Padding tokens are excluded.
        """

        mask = attention_mask.unsqueeze(-1).float()

        masked_hidden_states = (
            hidden_states * mask
        )

        token_count = mask.sum(
            dim=1
        ).clamp(
            min=1.0
        )

        pooled = (
            masked_hidden_states.sum(dim=1)
            / token_count
        )

        return pooled


    def forward(
        self,
        input_ids,
        attention_mask,
    ):
        """
        Forward pass.

        Parameters
        ----------
        input_ids:
            Tensor of shape [batch, sequence_length]

        attention_mask:
            Tensor of shape [batch, sequence_length]

        Returns
        -------
        logits:
            Tensor of shape [batch, num_labels]
        """

        # ----------------------------------------------------
        # Token embeddings
        # ----------------------------------------------------

        x = self.token_embedding(
            input_ids
        )

        # ----------------------------------------------------
        # Add positional information
        # ----------------------------------------------------

        x = self.position_encoding(
            x
        )

        # ----------------------------------------------------
        # Transformer padding mask
        #
        # Transformer expects:
        # True  = ignore token
        # False = valid token
        # ----------------------------------------------------

        padding_mask = (
            attention_mask == 0
        )

        # ----------------------------------------------------
        # Transformer
        # ----------------------------------------------------

        x = self.transformer(
            x,
            src_key_padding_mask=padding_mask,
        )

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        x = self.final_norm(
            x
        )

        # ----------------------------------------------------
        # Masked mean pooling
        # ----------------------------------------------------

        pooled = self.masked_mean_pooling(
            x,
            attention_mask,
        )

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        logits = self.classifier(
            pooled
        )

        return logits


# ============================================================
# MODEL INFORMATION
# ============================================================

def count_parameters(model):

    return sum(
        parameter.numel()
        for parameter in model.parameters()
    )


def count_trainable_parameters(model):

    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )


# ============================================================
# TEST MODEL
# ============================================================

def main():

    print("=" * 70)
    print("L.I.M.I.N.A.L. — ARCHAEOLOGIST MODEL TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Load tokenizer vocabulary
    # --------------------------------------------------------

    project_dir = (
        Path(__file__).resolve().parent.parent.parent
    )

    vocab_file = (
        project_dir
        / "models"
        / "archaeologist"
        / "tokenizer"
        / "vocab.json"
    )

    if not vocab_file.exists():

        print()
        print("ERROR: Vocabulary file not found.")
        print()
        print("Expected:")
        print(vocab_file)

        raise SystemExit(1)

    import json

    with open(
        vocab_file,
        "r",
        encoding="utf-8",
    ) as file:

        vocabulary = json.load(file)

    vocab_size = len(vocabulary)

    print()
    print(f"Vocabulary size : {vocab_size}")

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device          : {device}"
    )

    if torch.cuda.is_available():

        print(
            f"GPU             : "
            f"{torch.cuda.get_device_name(0)}"
        )

        print(
            f"CUDA            : "
            f"{torch.version.cuda}"
        )

    # --------------------------------------------------------
    # Create model
    # --------------------------------------------------------

    model = ArchaeologistModel(
        vocab_size=vocab_size,
        num_labels=7,
        embedding_dimension=256,
        num_attention_heads=8,
        num_transformer_layers=4,
        feed_forward_dimension=1024,
        max_sequence_length=128,
        dropout=0.1,
    )

    # --------------------------------------------------------
    # Parameter count
    # --------------------------------------------------------

    total_parameters = count_parameters(
        model
    )

    trainable_parameters = (
        count_trainable_parameters(model)
    )

    print()
    print(
        f"Total parameters     : "
        f"{total_parameters:,}"
    )

    print(
        f"Trainable parameters : "
        f"{trainable_parameters:,}"
    )

    # --------------------------------------------------------
    # Move to GPU
    # --------------------------------------------------------

    model = model.to(device)

    # --------------------------------------------------------
    # Dummy batch
    # --------------------------------------------------------

    batch_size = 8
    sequence_length = 128

    input_ids = torch.randint(
        low=0,
        high=vocab_size,
        size=(
            batch_size,
            sequence_length,
        ),
        device=device,
    )

    attention_mask = torch.ones(
        (
            batch_size,
            sequence_length,
        ),
        dtype=torch.long,
        device=device,
    )

    # Simulate padding in the last 20 tokens.
    attention_mask[:, -20:] = 0

    # --------------------------------------------------------
    # Forward pass
    # --------------------------------------------------------

    model.eval()

    with torch.no_grad():

        logits = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

    probabilities = torch.sigmoid(
        logits
    )

    print()
    print("=" * 70)
    print("FORWARD PASS")
    print("=" * 70)

    print()
    print(
        f"Input shape  : "
        f"{tuple(input_ids.shape)}"
    )

    print(
        f"Output shape : "
        f"{tuple(logits.shape)}"
    )

    print()
    print("Logits:")
    print(logits)

    print()
    print("Probabilities:")
    print(probabilities)

    # --------------------------------------------------------
    # GPU memory
    # --------------------------------------------------------

    if torch.cuda.is_available():

        torch.cuda.synchronize()

        allocated = (
            torch.cuda.memory_allocated()
            / (1024 ** 3)
        )

        reserved = (
            torch.cuda.memory_reserved()
            / (1024 ** 3)
        )

        print()
        print("GPU MEMORY")
        print("-" * 70)

        print(
            f"Allocated : {allocated:.3f} GB"
        )

        print(
            f"Reserved  : {reserved:.3f} GB"
        )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ARCHAEOLOGIST MODEL TEST PASSED")
    print("=" * 70)

    print()
    print("Model properties:")
    print("  Random initialization : YES")
    print("  Pretrained weights     : NO")
    print("  Pretrained encoder     : NO")
    print("  Multi-label output     : YES")
    print("  Number of labels       : 7")


if __name__ == "__main__":
    main()