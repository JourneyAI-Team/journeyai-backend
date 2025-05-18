#!/usr/bin/env python
import argparse
import asyncio
import time
from statistics import mean

from rich import print as rprint  # pretty console output

from app.db.init_db import init_db
from app.models.session import Session


def _parse_args() -> argparse.Namespace:  # noqa: D401
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Beanie/MongoDB micro-benchmark")
    parser.add_argument("--concurrency", type=int, default=100, help="Number of tasks")
    parser.add_argument("--duration", type=int, default=30, help="Seconds per test")
    return parser.parse_args()


async def _worker(stop_event: asyncio.Event, latencies: list[float]) -> None:
    """
    Execute a representative query in a tight loop until *stop_event* is set.

    The query chosen here is the same one used by the `/session/{id}` endpoint:
    filter by *id* + *organization_id*.
    """
    # Pre-fetch one random document id to avoid measuring “not-found” paths
    sample = await Session.find_one({})
    if not sample:
        return

    while not stop_event.is_set():
        t0 = time.perf_counter()
        _ = await Session.find_one(
            Session.id == sample.id, Session.organization_id == sample.organization_id
        )
        latencies.append(time.perf_counter() - t0)


async def run_benchmark() -> None:
    """
    Main entry-point.

    1. Warm-up the connection pool.
    2. Spawn *concurrency* workers for *duration* seconds.
    3. Gather timing statistics.
    """
    args = _parse_args()
    await init_db()

    stop = asyncio.Event()
    latencies: list[float] = []

    # Launch workers
    workers = [
        asyncio.create_task(_worker(stop, latencies)) for _ in range(args.concurrency)
    ]

    # Let them hammer the database
    await asyncio.sleep(args.duration)
    stop.set()
    await asyncio.gather(*workers, return_exceptions=True)

    if not latencies:
        rprint("[red]No latencies collected – is the DB empty?[/red]")
        return

    latencies.sort()
    p50 = latencies[int(0.5 * len(latencies))]
    p95 = latencies[int(0.95 * len(latencies))]
    report = {
        "total_ops": len(latencies),
        "avg_latency_ms": mean(latencies) * 1000,
        "p50_ms": p50 * 1000,
        "p95_ms": p95 * 1000,
        "max_ms": max(latencies) * 1000,
        "throughput_ops_s": len(latencies) / args.duration,
    }

    rprint(f"[bold green]Results[/bold green]\n{report}")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
