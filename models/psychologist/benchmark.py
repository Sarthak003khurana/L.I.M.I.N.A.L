import sys
import time
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.psychologist.model import PsychologistModel


def main():

    print("=" * 70)
    print("L.I.M.I.N.A.L. — M2 PSYCHOLOGIST GPU BENCHMARK")
    print("=" * 70)

    if not torch.cuda.is_available():
        print("\nCUDA is NOT available.")
        print("Benchmark cannot continue.")
        return

    device = torch.device("cuda")

    print(f"\nGPU       : {torch.cuda.get_device_name(0)}")
    print(f"CUDA      : {torch.version.cuda}")

    total_memory = (
        torch.cuda.get_device_properties(0).total_memory
        / (1024 ** 3)
    )

    print(f"VRAM      : {total_memory:.2f} GB")

    vocab_size = 216

    model = PsychologistModel(
        vocab_size=vocab_size
    ).to(device)

    model.train()

    total_parameters = sum(
        p.numel()
        for p in model.parameters()
    )

    print(
        f"\nParameters: {total_parameters:,}"
    )

    batch_size = 32
    sequence_length = 128
    steps = 50

    print(f"Batch size: {batch_size}")
    print(f"Sequence  : {sequence_length}")
    print(f"Steps     : {steps}")

    inputs = torch.randint(
        0,
        vocab_size,
        (
            batch_size,
            sequence_length,
        ),
        device=device,
    )

    targets = torch.randint(
        0,
        2,
        (
            batch_size,
            7,
        ),
        device=device,
    ).float()

    criterion = torch.nn.BCEWithLogitsLoss()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=3e-4,
        weight_decay=1e-4,
    )

    # Warm-up.
    print("\nWarm-up...")

    for _ in range(5):

        optimizer.zero_grad(
            set_to_none=True
        )

        output = model(inputs)

        loss = criterion(
            output,
            targets
        )

        loss.backward()

        optimizer.step()

    torch.cuda.synchronize()

    # Reset memory statistics.
    torch.cuda.reset_peak_memory_stats()

    print("Benchmarking...")

    start = time.perf_counter()

    for step in range(steps):

        optimizer.zero_grad(
            set_to_none=True
        )

        output = model(inputs)

        loss = criterion(
            output,
            targets
        )

        loss.backward()

        optimizer.step()

    torch.cuda.synchronize()

    end = time.perf_counter()

    total_time = end - start
    time_per_step = total_time / steps

    peak_memory = (
        torch.cuda.max_memory_allocated()
        / (1024 ** 3)
    )

    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)

    print(
        f"\nTotal time       : "
        f"{total_time:.3f} seconds"
    )

    print(
        f"Time per step    : "
        f"{time_per_step:.4f} seconds"
    )

    print(
        f"Steps per second : "
        f"{1 / time_per_step:.2f}"
    )

    print(
        f"Peak GPU memory  : "
        f"{peak_memory:.3f} GB"
    )

    print(
        f"VRAM utilization : "
        f"{(peak_memory / total_memory) * 100:.1f}%"
    )

    print("\n" + "=" * 70)
    print("M2 GPU BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
