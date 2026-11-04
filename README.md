# Assignment 3: Understanding Algorithm Efficiency and Scalability

**Author:** Soundarya Kavimani · MSCS-532-B01 Algorithms and Data Structures

**Repository:** https://github.com/skavimani/algorithm-efficiency-assignment3

This repository contains Python implementations of **Randomized Quicksort** and a
**hash table with chaining** (universal hashing plus dynamic resizing), the benchmark
code used to test them, and a report with the theoretical analysis and empirical results.

## Repository contents

| File | What it is |
|---|---|
| `quicksort.py` | Randomized Quicksort (uniform random pivot) and deterministic Quicksort (first-element pivot), both with three-way partitioning |
| `hash_table.py` | `HashTable` class: separate chaining, Carter–Wegman universal hash function, `insert` / `search` / `delete`, automatic grow/shrink |
| `demo_quicksort.py` | Shows both Quicksort versions on the edge cases (empty, single, sorted, reverse, repeated, negatives) |
| `compare_quicksort.py` | Quick (~2 s) timing and comparison-count table: randomized vs deterministic Quicksort |
| `demo_hash.py` | Shows insert, search, update, delete and automatic resizing of the hash table |
| `benchmark.py` | All experiments; writes CSV files and charts to `results/` |
| `tests/test_all.py` | 11 unit tests (edge cases for sorting, randomized check of the hash table against Python's `dict`) |
| `results/` | CSV data, charts (`*.png`) and console output from the run used in the report |
| `results/screenshots/` | Terminal screenshots of each program running (Figures 1, 2, 4 and 5 in the report) |
| `Assignment3_Report.docx` | Full report: analysis, empirical comparison, discussion, references |

## Requirements

* Python 3.8 or newer
* `matplotlib` (only needed to draw the charts): `pip install matplotlib`

## How to run

```bash
# Small demos
python3 quicksort.py
python3 demo_quicksort.py
python3 compare_quicksort.py
python3 hash_table.py
python3 demo_hash.py

# Unit tests
python3 -m unittest discover -s tests -v

# Benchmarks (full run takes about 2–3 minutes; --quick takes a few seconds)
python3 benchmark.py
python3 benchmark.py --quick
```

### Using the code

```python
from quicksort import randomized_quicksort
from hash_table import HashTable

data = [5, 3, 8, 1, 3]
randomized_quicksort(data)        # sorts in place -> [1, 3, 3, 5, 8]

t = HashTable()
t.insert("apple", 3)
t.search("apple")                 # -> 3
t.delete("apple")                 # -> True
```

## Summary of findings

**Randomized Quicksort**

* Its average number of comparisons matched the theoretical expectation 2(n+1)Hₙ − 4n ≈ 1.39 n log₂ n
  to within 1% for n = 100 to 100,000 (e.g. 155,867 measured vs 155,772 expected at n = 10,000).
* Its running time stayed O(n log n) on every input type: random, sorted, reverse-sorted and repeated values.
* Deterministic (first-element pivot) Quicksort hit its Θ(n²) worst case on sorted and reverse-sorted
  input. At n = 16,000 it made exactly n(n−1)/2 = 127,992,000 comparisons and took **3.2 s (sorted)
  and 11.3 s (reverse)**, compared with **0.04 s and 0.02 s** for the randomized version.
* On random input the deterministic version was about as fast or slightly faster, because there a
  first-element pivot is already a random pivot and it skips the random-number call.
* Three-way partitioning made arrays with many repeated values the fastest case for both versions.

**Hash table with chaining**

* The measured number of keys examined per search matched simple-uniform-hashing theory almost exactly:
  1 + α/2 for successful searches and α for unsuccessful ones (e.g. α = 16: 9.02 vs 9.0, and 16.03 vs 16).
* Search, insert and delete costs grow linearly with the load factor α.
* With dynamic resizing (double when α > 1, halve when α < ¼), search time stayed below 1 µs up to
  50,000 keys. Without resizing (8 fixed slots) it rose to 233 µs.

See `Assignment3_Report.docx` for the full analysis and discussion.
