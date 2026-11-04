from quicksort import randomized_quicksort, deterministic_quicksort

cases = {
    "Empty array":       [],
    "Single element":    [42],
    "Random":            [5, 3, 8, 1, 9, 2, 7],
    "Already sorted":    [1, 2, 3, 4, 5, 6, 7],
    "Reverse sorted":    [7, 6, 5, 4, 3, 2, 1],
    "Repeated elements": [4, 1, 4, 4, 2, 1, 4, 2],
    "Negatives":         [3, -1, 0, -7, 5, -1],
}

print("--- Edge cases ---")
for name, data in cases.items():
    r = randomized_quicksort(list(data))
    d = deterministic_quicksort(list(data))
    ok = "OK" if r == d == sorted(data) else "WRONG"
    print(f"{name:18s} {str(data):28s} -> {str(r):28s} {ok}")
