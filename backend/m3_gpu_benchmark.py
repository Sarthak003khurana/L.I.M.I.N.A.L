import sys
import time
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.logician.model import LogicianTransformer


VOCAB_SIZE = 318
BATCH_SIZE = 32
SEQ_LEN = 128
STEPS = 50


def main():

    print("=" * 60)
    print("M3 LOGICIAN GPU BENCHMARK")
    print("=" * 60)

    if not torch.cuda.is_available():
        print("CUDA is NOT available.")
        return

    device = torch.device("cuda")

    print(f"GPU: {torch.cuda.get_device_name(0)}")

    model = LogicianTransformer(
        vocab_size=VOCAB_SIZE
    ).to(device)

    model.train()

    input_ids = torch.randint(
        0,
        VOCAB_SIZE,
        (BATCH_SIZE, SEQ_LEN),
        device=device
    )

    attention_mask = torch.ones(
        (BATCH_SIZE, SEQ_LEN),
        dtype=torch.long,
        device=device
    )

    targets = torch.randint(
        0,
        2,
        (BATCH_SIZE, 6),
        dtype=torch.float32,
        device=device
    )

    criterion = torch.nn.BCEWithLogitsLoss()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=3e-4
    )

    print("\nRunning warm-up...")

    for _ in range(5):

        optimizer.zero_grad(
            set_to_none=True
        )

        output = model(
            input_ids,
            attention_mask
        )

        loss = criterion(
            output,
            targets
        )

        loss.backward()
        optimizer.step()

    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()

    print("Running benchmark...")

    start = time.perf_counter()

    for _ in range(STEPS):

        optimizer.zero_grad(
            set_to_none=True
        )

        output = model(
            input_ids,
            attention_mask
        )

        loss = criterion(
            output,
            targets
        )

        loss.backward()
        optimizer.step()

    torch.cuda.synchronize()

    elapsed = time.perf_counter() - start

    peak_memory = (
        torch.cuda.max_memory_allocated()
        / 1024**3
    )

    seconds_per_step = elapsed / STEPS
    steps_per_second = STEPS / elapsed

    print("\nResults:")
    print(f"  Batch size:       {BATCH_SIZE}")
    print(f"  Sequence length:  {SEQ_LEN}")
    print(f"  Steps:            {STEPS}")
    print(f"  Total time:       {elapsed:.3f} sec")
    print(f"  Time/step:        {seconds_per_step:.4f} sec")
    print(f"  Steps/second:     {steps_per_second:.2f}")
    print(f"  Peak GPU memory:  {peak_memory:.3f} GB")
    print(f"  VRAM used:        {peak_memory / 6.0 * 100:.1f}%")

    print("=" * 60)


if __name__ == "__main__":
    main()
