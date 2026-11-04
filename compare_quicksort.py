import math
import random
import time

from quicksort import randomized_quicksort, deterministic_quicksort

rng = random.Random(2026)


def make(kind, n):
    if kind == "Random":
        return [rng.randint(0, 10 * n) for _ in range(n)]
    if kind == "Sorted":
        return list(range(n))
    if kind == "Reverse":
        return list(range(n, 0, -1))
    return [rng.randint(0, 9) for _ in range(n)]  # Repeated: only 10 values


def run(sort_fn, data):
    arr = list(data)
    count = [0]
    start = time.perf_counter()
    sort_fn(arr, count)
    ms = (time.perf_counter() - start) * 1000
    assert arr == sorted(data)
    return ms, count[0]


print("--- Randomized vs Deterministic (first-element pivot) Quicksort ---")
print(f"{'Input':9s} {'n':>6s} {'Random ms':>10s} {'Determ. ms':>11s} "
      f"{'Random comps':>13s} {'Determ. comps':>14s}")
for kind in ["Random", "Sorted", "Reverse", "Repeated"]:
    for n in [1000, 2000, 4000]:
        data = make(kind, n)
        r_ms, r_c = run(lambda a, c: randomized_quicksort(a, rng, c), data)
        d_ms, d_c = run(lambda a, c: deterministic_quicksort(a, c), data)
        print(f"{kind:9s} {n:6d} {r_ms:10.2f} {d_ms:11.2f} {r_c:13,d} {d_c:14,d}")

print("\n--- Average comparisons of Randomized Quicksort vs theory ---")
print(f"{'n':>7s} {'measured (avg of 20)':>21s} {'theory 2(n+1)H_n - 4n':>23s}")
for n in [100, 1000, 10000]:
    total = 0
    for _ in range(20):
        c = [0]
        randomized_quicksort(rng.sample(range(10 * n), n), rng, c)
        total += c[0]
    h_n = sum(1 / k for k in range(1, n + 1))
    print(f"{n:7d} {total / 20:21,.0f} {2 * (n + 1) * h_n - 4 * n:23,.0f}")
