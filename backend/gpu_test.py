import torch
import torch.nn as nn
import time

print("=" * 50)
print("L.I.M.I.N.A.L. GPU TEST")
print("=" * 50)

device = torch.device("cuda")

print("GPU:", torch.cuda.get_device_name(0))
print(
    "VRAM:",
    round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
    "GB"
)


class TestModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.embedding = nn.Embedding(16000, 512)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=512,
            nhead=8,
            dim_feedforward=2048,
            batch_first=True,
            norm_first=True
        )

        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=8
        )

        self.classifier = nn.Linear(512, 7)

    def forward(self, x):
        x = self.embedding(x)
        x = self.encoder(x)
        x = x.mean(dim=1)
        return self.classifier(x)


model = TestModel().to(device)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=3e-4
)

criterion = nn.CrossEntropyLoss()

batch_size = 8
sequence_length = 128

x = torch.randint(
    0,
    16000,
    (batch_size, sequence_length),
    device=device
)

y = torch.randint(
    0,
    7,
    (batch_size,),
    device=device
)


# Warmup
for _ in range(3):
    optimizer.zero_grad()

    output = model(x)

    loss = criterion(output, y)

    loss.backward()

    optimizer.step()


torch.cuda.synchronize()


# Actual benchmark
start = time.time()

for step in range(20):

    optimizer.zero_grad()

    output = model(x)

    loss = criterion(output, y)

    loss.backward()

    optimizer.step()


torch.cuda.synchronize()

elapsed = time.time() - start

memory_used = torch.cuda.max_memory_allocated() / 1024**3


print()
print("=" * 50)
print("RESULT")
print("=" * 50)

print(
    "Model parameters:",
    round(sum(p.numel() for p in model.parameters()) / 1e6, 2),
    "M"
)

print("Batch size:", batch_size)
print("Sequence length:", sequence_length)

print(
    "Peak VRAM:",
    round(memory_used, 2),
    "GB"
)

print(
    "20 steps:",
    round(elapsed, 2),
    "seconds"
)

print(
    "Time / step:",
    round(elapsed / 20, 3),
    "seconds"
)

print()
print("GPU TEST COMPLETE")