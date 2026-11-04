"""
Empirical experiments for Assignment 3.

    python benchmark.py            # full run (a few minutes)
    python benchmark.py --quick    # smaller sizes, finishes in seconds

Writes CSV files and PNG charts to the results/ folder.
"""

import argparse
import csv
import math
import os
import random
import statistics
import sys
import time

from quicksort import randomized_quicksort, deterministic_quicksort
from hash_table import HashTable

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ----------------------------------------------------------------------
# Part 1: Quicksort
# ----------------------------------------------------------------------
def make_input(kind, n, rng):
    if kind == "random":
        return [rng.randint(0, 10 * n) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "repeated":
        return [rng.randint(0, 9) for _ in range(n)]  # only 10 distinct values
    raise ValueError(kind)


def time_sort(sort_fn, data, repeats):
    times = []
    for _ in range(repeats):
        arr = list(data)
        t0 = time.perf_counter()
        sort_fn(arr)
        times.append(time.perf_counter() - t0)
        assert arr == sorted(data)
    return statistics.median(times)


def quicksort_experiment(sizes, repeats):
    rng = random.Random(2026)
    rows = []
    for kind in ["random", "sorted", "reverse", "repeated"]:
        for n in sizes:
            data = make_input(kind, n, rng)
            t_rand = time_sort(lambda a: randomized_quicksort(a, rng), data, repeats)
            t_det = time_sort(deterministic_quicksort, data, repeats)
            c_rand, c_det = [0], [0]
            randomized_quicksort(list(data), rng, c_rand)
            deterministic_quicksort(list(data), c_det)
            rows.append(dict(distribution=kind, n=n,
                             randomized_ms=round(t_rand * 1000, 3),
                             deterministic_ms=round(t_det * 1000, 3),
                             randomized_comparisons=c_rand[0],
                             deterministic_comparisons=c_det[0]))
            print(f"  {kind:9s} n={n:6d}  randomized {t_rand*1000:9.2f} ms   "
                  f"deterministic {t_det*1000:10.2f} ms", flush=True)
    return rows


def comparison_count_experiment(sizes, trials):
    """Average comparisons of randomized quicksort vs. the exact expectation
    2(n+1)H_n - 4n for distinct keys."""
    rng = random.Random(7)
    rows = []
    for n in sizes:
        counts = []
        for _ in range(trials):
            data = rng.sample(range(10 * n), n)  # distinct keys
            c = [0]
            randomized_quicksort(data, rng, c)
            counts.append(c[0])
        h_n = sum(1 / k for k in range(1, n + 1))
        expected = 2 * (n + 1) * h_n - 4 * n
        rows.append(dict(n=n, mean_comparisons=round(statistics.mean(counts), 1),
                         stdev=round(statistics.stdev(counts), 1),
                         theory_exact=round(expected, 1),
                         two_n_ln_n=round(2 * n * math.log(n), 1)))
    return rows


# ----------------------------------------------------------------------
# Part 2: Hash table
# ----------------------------------------------------------------------
def load_factor_experiment(m, alphas, probes):
    """Fixed table size m, resizing OFF; vary alpha = n/m."""
    rng = random.Random(11)
    rows = []
    for alpha in alphas:
        n = int(alpha * m)
        t = HashTable(capacity=m, resize=False, seed=rng.random())
        keys = rng.sample(range(10 ** 9), n + probes)
        present, absent = keys[:n], keys[n:]
        t0 = time.perf_counter()
        for k in present:
            t.insert(k, k)
        t_ins = (time.perf_counter() - t0) / n

        hits = rng.choices(present, k=probes)
        t0 = time.perf_counter()
        for k in hits:
            t.search(k)
        t_hit = (time.perf_counter() - t0) / probes

        t0 = time.perf_counter()
        for k in absent:
            t.search(k)
        t_miss = (time.perf_counter() - t0) / probes

        # Machine-independent cost: keys examined per search
        hit_probes = statistics.mean(
            [k for k, _ in t._buckets[t._index(key)]].index(key) + 1 for key in hits)
        miss_probes = statistics.mean(len(t._buckets[t._index(key)]) for key in absent)

        lengths = t.chain_lengths()
        rows.append(dict(alpha=alpha, n=n, m=m,
                         hit_probes=round(hit_probes, 3), theory_hit=round(1 + alpha / 2, 3),
                         miss_probes=round(miss_probes, 3), theory_miss=alpha,
                         insert_us=round(t_ins * 1e6, 3),
                         search_hit_us=round(t_hit * 1e6, 3),
                         search_miss_us=round(t_miss * 1e6, 3),
                         mean_chain=round(statistics.mean(lengths), 3),
                         longest_chain=max(lengths)))
        print(f"  alpha={alpha:5.2f}  hit {t_hit*1e6:6.2f} us  miss {t_miss*1e6:6.2f} us"
              f"  longest chain {max(lengths)}", flush=True)
    return rows


def resizing_experiment(n_total, checkpoints):
    """Insert n_total keys into a table that starts with 8 slots, with and
    without dynamic resizing; time searches at each checkpoint."""
    rng = random.Random(13)
    keys = rng.sample(range(10 ** 9), n_total)
    rows = []
    for resize in (True, False):
        t = HashTable(capacity=8, resize=resize, seed=1)
        done = 0
        for cp in checkpoints:
            for k in keys[done:cp]:
                t.insert(k, k)
            done = cp
            sample = rng.choices(keys[:cp], k=2000)
            t0 = time.perf_counter()
            for k in sample:
                t.search(k)
            rows.append(dict(resizing="on" if resize else "off", n=cp,
                             slots=t.capacity, load_factor=round(t.load_factor, 3),
                             search_us=round((time.perf_counter() - t0) / 2000 * 1e6, 3)))
    return rows


def delete_experiment(m, alphas, probes):
    rng = random.Random(17)
    rows = []
    for alpha in alphas:
        n = int(alpha * m)
        t = HashTable(capacity=m, resize=False, seed=rng.random())
        keys = rng.sample(range(10 ** 9), n)
        for k in keys:
            t.insert(k, k)
        victims = keys[:probes]
        t0 = time.perf_counter()
        for k in victims:
            t.delete(k)
        rows.append(dict(alpha=alpha, delete_us=round((time.perf_counter() - t0) / len(victims) * 1e6, 3)))
    return rows


# ----------------------------------------------------------------------
def write_csv(name, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def make_charts(qs, lf, rs):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping charts")
        return

    # Quicksort: one panel per distribution
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5))
    titles = {"random": "Random array", "sorted": "Already sorted",
              "reverse": "Reverse sorted", "repeated": "Repeated elements (10 values)"}
    for ax, kind in zip(axes.flat, titles):
        r = [x for x in qs if x["distribution"] == kind]
        ns = [x["n"] for x in r]
        ax.plot(ns, [x["randomized_ms"] for x in r], "o-", color="#2563eb", label="Randomized pivot")
        ax.plot(ns, [x["deterministic_ms"] for x in r], "s--", color="#dc2626", label="First-element pivot")
        ax.set_title(titles[kind])
        ax.set_xlabel("n (array size)")
        ax.set_ylabel("time (ms)")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Randomized vs. deterministic Quicksort (median of runs)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "quicksort_comparison.png"), dpi=150)
    plt.close(fig)

    # Hash table: probes vs theory, and time vs load factor
    fig, (ax0, ax) = plt.subplots(1, 2, figsize=(11, 4.5))
    a = [x["alpha"] for x in lf]
    ax0.plot(a, [x["hit_probes"] for x in lf], "o", color="#2563eb", label="Successful search (measured)")
    ax0.plot(a, [x["theory_hit"] for x in lf], "-", color="#2563eb", alpha=0.6, label="Theory 1 + α/2")
    ax0.plot(a, [x["miss_probes"] for x in lf], "s", color="#dc2626", label="Unsuccessful search (measured)")
    ax0.plot(a, [x["theory_miss"] for x in lf], "-", color="#dc2626", alpha=0.6, label="Theory α")
    ax0.set_xlabel("load factor  α = n / m")
    ax0.set_ylabel("keys examined per search")
    ax0.set_title("Keys examined vs. theory")
    ax0.grid(alpha=0.3)
    ax0.legend(fontsize=8)
    ax.plot(a, [x["search_hit_us"] for x in lf], "o-", color="#2563eb", label="Successful search")
    ax.plot(a, [x["search_miss_us"] for x in lf], "s-", color="#dc2626", label="Unsuccessful search")
    ax.plot(a, [x["insert_us"] for x in lf], "^-", color="#16a34a", label="Insert (avg over fill)")
    ax.set_xlabel("load factor  α = n / m")
    ax.set_ylabel("time per operation (µs)")
    ax.set_title("Measured time per operation")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "hash_load_factor.png"), dpi=150)
    plt.close(fig)

    # Resizing on vs off
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for mode, color, mk in (("on", "#2563eb", "o-"), ("off", "#dc2626", "s--")):
        r = [x for x in rs if x["resizing"] == mode]
        ax.plot([x["n"] for x in r], [x["search_us"] for x in r], mk, color=color,
                label=f"Resizing {mode}")
    ax.set_xscale("log")
    ax.set_xlabel("number of keys n (table starts with 8 slots)")
    ax.set_ylabel("search time (µs)")
    ax.set_title("Dynamic resizing keeps search time constant")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "hash_resizing.png"), dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="small sizes for a fast run")
    args = ap.parse_args()
    global OUT
    if args.quick:  # keep quick runs separate from the full results used in the report
        OUT = os.path.join(OUT, "quick")
    os.makedirs(OUT, exist_ok=True)
    sys.setrecursionlimit(10000)

    if args.quick:
        sizes, repeats = [250, 500, 1000, 2000], 3
        cmp_sizes, trials = [100, 1000], 20
        m, probes, n_total = 256, 2000, 20000
        checkpoints = [100, 1000, 5000, 20000]
    else:
        sizes, repeats = [1000, 2000, 4000, 8000, 16000], 5
        cmp_sizes, trials = [100, 1000, 10000, 100000], 30
        m, probes, n_total = 4096, 20000, 50000
        checkpoints = [100, 1000, 5000, 10000, 20000, 50000]

    print("Part 1: Quicksort timing")
    qs = quicksort_experiment(sizes, repeats)
    write_csv("quicksort_times.csv", qs)

    print("Part 1: comparison counts vs theory")
    cc = comparison_count_experiment(cmp_sizes, trials)
    write_csv("quicksort_comparisons.csv", cc)
    for r in cc:
        print("  ", r)

    alphas = [0.25, 0.5, 1, 2, 4, 8, 16]
    print("Part 2: hash table vs load factor")
    lf = load_factor_experiment(m, alphas, probes)
    write_csv("hash_load_factor.csv", lf)
    dl = delete_experiment(m, alphas, min(probes, int(0.25 * m)))
    write_csv("hash_delete.csv", dl)

    print("Part 2: dynamic resizing on vs off")
    rs = resizing_experiment(n_total, checkpoints)
    write_csv("hash_resizing.csv", rs)
    for r in rs:
        print("  ", r)

    make_charts(qs, lf, rs)
    print(f"\nResults written to {OUT}")


if __name__ == "__main__":
    main()
