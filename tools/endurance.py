#!/usr/bin/env python3
"""Accelerated seeded endurance checks with bounded-state and allocation evidence."""

from __future__ import annotations

import argparse
import gc
import json
import math
from pathlib import Path
import random
import statistics
import sys
import time
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from terminal_cells import World, render  # noqa: E402


def check_world(world):
    assert len(world.cells) <= 8
    assert len(world.bacteria) <= world._limits()[1] * 2
    assert len(world.phages) <= world._phage_limit()
    assert len(world.nutrients) <= 4
    assert len(world.hyphae) <= world._hypha_limit()
    for hypha in world.hyphae:
        assert len(hypha.nodes) <= 48
    for entity in [
        *world.cells,
        *world.bacteria.values(),
        *world.phages.values(),
        *world.red_cells,
        *world.debris,
        *world.spent_capsids,
    ]:
        assert math.isfinite(entity.x) and math.isfinite(entity.y)
    for cell in world.cells:
        if cell.target is not None:
            assert cell.target in world.bacteria


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--steps", type=int, default=108000)
    cli.add_argument("--seed", type=int, default=42)
    cli.add_argument("--scene", choices=["mixed", "blood", "microbial"], default="mixed")
    cli.add_argument("--output", type=Path, default=Path("endurance.json"))
    args = cli.parse_args()
    if args.steps < 1800:
        cli.error("--steps must be at least 1800 (one simulated minute)")
    world = World(120, 40, args.seed, scene=args.scene)
    rng = random.Random(args.seed)
    for _ in range(900):
        world.update()
    gc.collect()
    tracemalloc.start(1)
    baseline = tracemalloc.get_traced_memory()[0]
    latencies, counts = [], []
    for step in range(args.steps):
        start = time.perf_counter()
        world.update()
        if step % 60 == 0:
            latencies.append(time.perf_counter() - start)
        if step % 300 == 0:
            check_world(world)
            render(world)
            counts.append(len(world.bacteria))
        if step % 1800 == 0:
            world.resize(*rng.choice([(80, 24), (120, 40), (200, 60)]))
        if step % 900 == 0:
            world.lab.stir(
                world,
                rng.randrange(max(1, int(world.width))),
                rng.randrange(max(1, int(world.height / 2))),
            )
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    first = statistics.median(latencies[: max(1, len(latencies) // 5)])
    last = statistics.median(latencies[-max(1, len(latencies) // 5) :])
    report = dict(
        seed=args.seed,
        scene=args.scene,
        steps=args.steps,
        allocation_growth=current - baseline,
        peak_bytes=peak,
        update_first_median_ms=first * 1000,
        update_last_median_ms=last * 1000,
        microbe_samples=counts,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "microbe_samples"}, indent=2))
    assert peak < 128 * 1024 * 1024, "Excessive tracked allocation"
    assert current - baseline < 32 * 1024 * 1024, "Possible memory retention"
    assert last < max(0.1, first * 20), "Severe update-latency regression"
    assert any(counts[len(counts) // 2 :]), "Microbial population stayed extinct"


if __name__ == "__main__":
    main()
