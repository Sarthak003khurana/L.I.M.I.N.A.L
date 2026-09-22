import torch
import torch.nn as nn


class LogicianTransformer(nn.Module):

    def __init__(
        self,
        vocab_size,
        num_labels=6,
        embedding_dim=192,
        num_heads=6,
        num_layers=3,
        feedforward_dim=768,
        max_seq_len=128,
        dropout=0.30
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.num_labels = num_labels
        self.embedding_dim = embedding_dim
        self.max_seq_len = max_seq_len

        # --------------------------------------------------
        # Token embedding
        # --------------------------------------------------

        self.token_embedding = nn.Embedding(
            vocab_size,
            embedding_dim,
            padding_idx=0
        )

        # --------------------------------------------------
        # Positional embedding
        # --------------------------------------------------

        self.position_embedding = nn.Embedding(
            max_seq_len,
            embedding_dim
        )

        # --------------------------------------------------
        # Transformer encoder
        # --------------------------------------------------

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=feedforward_dim,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True
        )

        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )

        # --------------------------------------------------
        # Regularization
        # --------------------------------------------------

        self.dropout = nn.Dropout(dropout)

        # --------------------------------------------------
        # Classification head
        # --------------------------------------------------

        self.classifier = nn.Sequential(
            nn.Linear(
                embedding_dim,
                embedding_dim
            ),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(
                embedding_dim,
                num_labels
            )
        )

        # --------------------------------------------------
        # From-scratch initialization
        # --------------------------------------------------

        self._initialize_weights()

    def _initialize_weights(self):

        # Explicit random initialization.
        # No pretrained weights are used.

        nn.init.normal_(
            self.token_embedding.weight,
            mean=0.0,
            std=0.02
        )

        nn.init.normal_(
            self.position_embedding.weight,
            mean=0.0,
            std=0.02
        )

        for module in self.modules():

            if isinstance(module, nn.Linear):

                nn.init.xavier_uniform_(
                    module.weight
                )

                if module.bias is not None:

                    nn.init.zeros_(
                        module.bias
                    )

            elif isinstance(
                module,
                nn.LayerNorm
            ):

                nn.init.ones_(
                    module.weight
                )

                nn.init.zeros_(
                    module.bias
                )

    def forward(
        self,
        input_ids,
        attention_mask=None
    ):

        batch_size, seq_len = input_ids.shape

        if seq_len > self.max_seq_len:

            raise ValueError(
                f"Sequence length {seq_len} "
                f"exceeds maximum "
                f"{self.max_seq_len}"
            )

        # --------------------------------------------------
        # Position IDs
        # --------------------------------------------------

        positions = torch.arange(
            seq_len,
            device=input_ids.device
        ).unsqueeze(0)

        # --------------------------------------------------
        # Token + position embeddings
        # --------------------------------------------------

        x = (
            self.token_embedding(input_ids)
            + self.position_embedding(positions)
        )

        x = self.dropout(x)

        # --------------------------------------------------
        # Padding mask
        #
        # True = ignore padding position
        # --------------------------------------------------

        padding_mask = None

        if attention_mask is not None:

            padding_mask = (
                attention_mask == 0
            )

        # --------------------------------------------------
        # Transformer
        # --------------------------------------------------

        x = self.encoder(
            x,
            src_key_padding_mask=padding_mask
        )

        # --------------------------------------------------
        # Masked mean pooling
        # --------------------------------------------------

        if attention_mask is not None:

            mask = (
                attention_mask
                .unsqueeze(-1)
                .float()
            )

            x = x * mask

            summed = x.sum(
                dim=1
            )

            counts = mask.sum(
                dim=1
            ).clamp(min=1.0)

            pooled = summed / counts

        else:

            pooled = x.mean(
                dim=1
            )

        pooled = self.dropout(
            pooled
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        logits = self.classifier(
            pooled
        )

        return logits


def count_parameters(model):

    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )


if __name__ == "__main__":

    vocab_size = 466

    model = LogicianTransformer(
        vocab_size=vocab_size
    )

    print("=" * 60)
    print("M3 LOGICIAN TRANSFORMER")
    print("=" * 60)

    print(
        f"Vocabulary size: {vocab_size}"
    )

    print(
        f"Parameters: "
        f"{count_parameters(model):,}"
    )

    device = (
        torch.device("cuda")
        if torch.cuda.is_available()
        else torch.device("cpu")
    )

    print(
        f"Device: {device}"
    )

    model = model.to(device)

    input_ids = torch.randint(
        0,
        vocab_size,
        (8, 128),
        device=device
    )

    attention_mask = torch.ones(
        (8, 128),
        device=device
    )

    with torch.no_grad():

        output = model(
            input_ids,
            attention_mask
        )

    print(
        f"Input shape:  "
        f"{tuple(input_ids.shape)}"
    )

    print(
        f"Output shape: "
        f"{tuple(output.shape)}"
    )

    if device.type == "cuda":

        allocated = (
            torch.cuda.memory_allocated()
            / 1024**3
        )

        reserved = (
            torch.cuda.memory_reserved()
            / 1024**3
        )

        print(
            f"GPU allocated: "
            f"{allocated:.3f} GB"
        )

        print(
            f"GPU reserved:  "
            f"{reserved:.3f} GB"
        )

    print("=" * 60)