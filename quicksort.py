"""
Randomized and deterministic Quicksort.

Both versions use the same single-pass three-way partition
(< pivot | == pivot | > pivot), so the ONLY difference between them is how the
pivot is chosen:

    * randomized_quicksort    -> pivot chosen uniformly at random
    * deterministic_quicksort -> pivot is always the first element

Edge cases handled:
    * empty arrays and single-element arrays (returned immediately)
    * arrays with many repeated elements (three-way partition puts every copy
      of the pivot in its final place at once, so duplicates do not cause
      quadratic behaviour)
    * already-sorted / reverse-sorted arrays (randomized pivot makes these
      no worse than any other input; recursion always goes into the SMALLER
      side and loops on the larger side, so the stack depth stays O(log n)
      even when the deterministic version hits its worst case)
"""

import random


def _three_way_partition(arr, lo, hi, pivot_index):
    """Rearrange arr[lo..hi] into  < pivot | == pivot | > pivot.

    Returns (lt, gt) such that arr[lt..gt] all equal the pivot value.

    One left-to-right scan keeps three regions behind the cursor i:
        arr[lo .. lt-1]  < pivot
        arr[lt .. eq-1] == pivot
        arr[eq .. i-1]   > pivot
    Elements larger than the pivot are never moved, so the relative order of
    the "> pivot" part is preserved (like the textbook Lomuto partition).
    That keeps the classic worst case of the first-element pivot visible on
    already-sorted input, which makes the comparison with the randomized
    version fair.
    """
    arr[lo], arr[pivot_index] = arr[pivot_index], arr[lo]
    pivot = arr[lo]
    lt = eq = lo
    for i in range(lo, hi + 1):
        x = arr[i]
        if x > pivot:
            continue
        arr[i] = arr[eq]
        if x < pivot:
            arr[eq] = arr[lt]
            arr[lt] = x
            lt += 1
        else:
            arr[eq] = x
        eq += 1
    return lt, eq - 1


def _quicksort(arr, lo, hi, choose_pivot, counter=None):
    # Loop instead of recursing on the larger side (tail-call elimination).
    while lo < hi:
        if counter is not None:
            counter[0] += hi - lo  # each non-pivot element is compared to the pivot
        p = choose_pivot(lo, hi)
        lt, gt = _three_way_partition(arr, lo, hi, p)
        if (lt - lo) < (hi - gt):
            _quicksort(arr, lo, lt - 1, choose_pivot, counter)
            lo = gt + 1
        else:
            _quicksort(arr, gt + 1, hi, choose_pivot, counter)
            hi = lt - 1


def randomized_quicksort(arr, rng=None, counter=None):
    """Sort arr in place using a pivot chosen uniformly at random.

    counter: optional one-element list; the number of element-vs-pivot
    comparisons is added to counter[0] (used by the benchmarks).
    Returns the same list for convenience.
    """
    if arr is None or len(arr) < 2:
        return arr
    rng = rng or random.Random()
    _quicksort(arr, 0, len(arr) - 1, lambda lo, hi: rng.randint(lo, hi), counter)
    return arr


def deterministic_quicksort(arr, counter=None):
    """Sort arr in place, always using the first element as the pivot."""
    if arr is None or len(arr) < 2:
        return arr
    _quicksort(arr, 0, len(arr) - 1, lambda lo, hi: lo, counter)
    return arr


if __name__ == "__main__":
    data = [5, 3, 8, 1, 9, 3, 3, 0, -2, 7]
    print("Input:        ", data)
    print("Randomized:   ", randomized_quicksort(list(data)))
    print("Deterministic:", deterministic_quicksort(list(data)))
