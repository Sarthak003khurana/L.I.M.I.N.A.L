import torch
import torch.nn as nn


class PsychologistModel(nn.Module):
    """
    L.I.M.I.N.A.L. M2 — Psychologist

    A separately trained Transformer classifier.

    This model:
    - Uses a tokenizer trained from scratch.
    - Uses randomly initialized weights.
    - Does not use a pretrained language model.
    - Predicts 7 psychological/affective communication labels.
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

        # Convert token IDs into dense vectors.
        self.token_embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dimension,
            padding_idx=0,
        )

        # Learn a representation for each position in the sentence.
        self.position_embedding = nn.Embedding(
            num_embeddings=max_sequence_length,
            embedding_dim=embedding_dimension,
        )

        # Transformer encoder.
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
            encoder_layer,
            num_layers=num_transformer_layers,
        )

        self.final_norm = nn.LayerNorm(
            embedding_dimension
        )

        # Classification head.
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

        # Random initialization.
        self._initialize_weights()

    def _initialize_weights(self):
        """
        Initialize all learnable parameters from scratch.

        No pretrained weights are loaded.
        """

        # Token embeddings.
        nn.init.normal_(
            self.token_embedding.weight,
            mean=0.0,
            std=0.02,
        )

        # Position embeddings.
        nn.init.normal_(
            self.position_embedding.weight,
            mean=0.0,
            std=0.02,
        )

        # Linear and normalization layers.
        for module in self.modules():

            if isinstance(module, nn.Linear):

                nn.init.xavier_uniform_(
                    module.weight
                )

                if module.bias is not None:
                    nn.init.zeros_(
                        module.bias
                    )

            elif isinstance(module, nn.LayerNorm):

                nn.init.ones_(
                    module.weight
                )

                nn.init.zeros_(
                    module.bias
                )

    def forward(self, input_ids):
        """
        Forward pass.

        Parameters
        ----------
        input_ids:
            Tensor of shape:
            (batch_size, sequence_length)

        Returns
        -------
        logits:
            Tensor of shape:
            (batch_size, num_labels)
        """

        batch_size, sequence_length = input_ids.shape

        # Prevent sequences longer than the model supports.
        if sequence_length > self.max_sequence_length:
            raise ValueError(
                f"Sequence length {sequence_length} exceeds "
                f"maximum {self.max_sequence_length}"
            )

        device = input_ids.device

        # Create position IDs.
        positions = torch.arange(
            sequence_length,
            device=device,
        )

        positions = positions.unsqueeze(0).expand(
            batch_size,
            -1,
        )

        # Token embedding + positional embedding.
        x = (
            self.token_embedding(input_ids)
            + self.position_embedding(positions)
        )

        # Padding token ID is 0.
        padding_mask = input_ids.eq(0)

        # Transformer processing.
        x = self.transformer(
            x,
            src_key_padding_mask=padding_mask,
        )

        x = self.final_norm(x)

        # Ignore padding tokens during pooling.
        valid_tokens = (
            (~padding_mask)
            .unsqueeze(-1)
            .float()
        )

        token_sum = (
            x * valid_tokens
        ).sum(dim=1)

        token_count = (
            valid_tokens
            .sum(dim=1)
            .clamp(min=1.0)
        )

        # One vector representing the whole sentence.
        pooled = token_sum / token_count

        # Seven psychological labels.
        logits = self.classifier(
            pooled
        )

        return logits


# ---------------------------------------------------------
# MODEL TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("L.I.M.I.N.A.L. — M2 PSYCHOLOGIST MODEL TEST")
    print("=" * 70)

    # Automatically use GPU if available.
    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"\nDevice: {device}")

    if torch.cuda.is_available():

        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

        print(
            f"CUDA: "
            f"{torch.version.cuda}"
        )

    # Our M2 tokenizer contains 216 vocabulary entries.
    vocab_size = 216

    model = PsychologistModel(
        vocab_size=vocab_size
    ).to(device)

    # Count parameters.
    total_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    print(
        f"\nTotal parameters     : "
        f"{total_parameters:,}"
    )

    print(
        f"Trainable parameters : "
        f"{trainable_parameters:,}"
    )

    # Dummy batch.
    batch_size = 8
    sequence_length = 128

    dummy_input = torch.randint(
        low=0,
        high=vocab_size,
        size=(
            batch_size,
            sequence_length,
        ),
        device=device,
    )

    # Forward pass.
    with torch.no_grad():

        output = model(
            dummy_input
        )

    print(
        f"\nInput shape  : "
        f"{tuple(dummy_input.shape)}"
    )

    print(
        f"Output shape : "
        f"{tuple(output.shape)}"
    )

    # GPU memory information.
    if torch.cuda.is_available():

        allocated = (
            torch.cuda.memory_allocated(
                device
            )
            / (1024 ** 3)
        )

        reserved = (
            torch.cuda.memory_reserved(
                device
            )
            / (1024 ** 3)
        )

        print(
            f"\nGPU allocated : "
            f"{allocated:.3f} GB"
        )

        print(
            f"GPU reserved  : "
            f"{reserved:.3f} GB"
        )

    print("\n" + "=" * 70)

    print(
        "M2 MODEL FORWARD PASS SUCCESSFUL"
    )

    print("=" * 70)