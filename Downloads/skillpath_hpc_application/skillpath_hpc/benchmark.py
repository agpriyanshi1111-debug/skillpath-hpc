"""Repeatable local sequential-vs-threaded benchmark for SkillPath."""
import argparse
import json
import os
import platform
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.recommender import recommend

def make_profile(i):
    return {
        "career_goal": ["AI/ML Engineer", "Data Scientist", "Software Developer", "Web Developer"][i % 4],
        "skills": {"Python Programming": i % 4, "SQL and Data Storage": (i + 1) % 4},
        "interests": [["python", "ai"], ["data", "statistics"], ["programming", "dsa"], ["web", "javascript"]][i % 4],
        "hours_per_week": 4 + (i % 8),
        "timeframe_weeks": 8 + (i % 12)
    }

def run(profiles, repeats):
    inputs = [make_profile(i) for i in range(profiles)]
    seq_times, thread_times = [], []
    workers = min(8, os.cpu_count() or 2)
    for _ in range(repeats):
        t0 = time.perf_counter()
        seq = [len(recommend(p, limit=12)) for p in inputs]
        seq_times.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            threaded = list(pool.map(lambda p: len(recommend(p, limit=12)), inputs))
        thread_times.append(time.perf_counter() - t0)
        if seq != threaded:
            raise RuntimeError("Sequential and threaded outputs differ.")
    seq_avg = statistics.mean(seq_times)
    thread_avg = statistics.mean(thread_times)
    result = {
        "profiles": profiles, "repeats": repeats, "workers": workers,
        "environment": {"python": sys.version, "os": platform.platform(), "cpu_count": os.cpu_count()},
        "sequential_seconds_each_run": [round(x, 6) for x in seq_times],
        "threaded_seconds_each_run": [round(x, 6) for x in thread_times],
        "sequential_average_seconds": round(seq_avg, 6),
        "threaded_average_seconds": round(thread_avg, 6),
        "sequential_profiles_per_second": round(profiles / seq_avg, 2) if seq_avg else None,
        "threaded_profiles_per_second": round(profiles / thread_avg, 2) if thread_avg else None,
        "threaded_speedup": round(seq_avg / thread_avg, 3) if thread_avg else None,
        "interpretation": "Measured local result only. Threading may be slower for CPU-bound Python work; this is not a cluster-scale result."
    }
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", nargs="+", type=int, default=[100, 500, 1000])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", default="benchmark_results.json")
    args = parser.parse_args()
    if any(x < 1 or x > 20000 for x in args.profiles) or not 1 <= args.repeats <= 10:
        parser.error("profiles must be 1..20000 and repeats 1..10")
    results = [run(n, args.repeats) for n in args.profiles]
    out = {"results": results}
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print(f"\nSaved measured results to {Path(args.output).resolve()}")

if __name__ == "__main__":
    main()
