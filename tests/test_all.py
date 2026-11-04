import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quicksort import randomized_quicksort, deterministic_quicksort  # noqa: E402
from hash_table import HashTable  # noqa: E402


class TestQuicksort(unittest.TestCase):
    CASES = {
        "empty": [],
        "single": [42],
        "two": [2, 1],
        "sorted": list(range(1000)),
        "reverse": list(range(1000, 0, -1)),
        "all_equal": [7] * 1000,
        "few_distinct": [random.randint(0, 3) for _ in range(1000)],
        "negatives": [random.randint(-500, 500) for _ in range(1000)],
        "floats": [random.random() for _ in range(500)],
        "strings": ["pear", "apple", "fig", "apple", "kiwi"],
    }

    def test_randomized(self):
        for name, data in self.CASES.items():
            with self.subTest(case=name):
                self.assertEqual(randomized_quicksort(list(data)), sorted(data))

    def test_deterministic(self):
        for name, data in self.CASES.items():
            with self.subTest(case=name):
                self.assertEqual(deterministic_quicksort(list(data)), sorted(data))

    def test_sorts_in_place(self):
        data = [3, 1, 2]
        randomized_quicksort(data)
        self.assertEqual(data, [1, 2, 3])

    def test_random_stress(self):
        rng = random.Random(0)
        for _ in range(200):
            data = [rng.randint(0, 50) for _ in range(rng.randint(0, 200))]
            self.assertEqual(randomized_quicksort(list(data)), sorted(data))

    def test_large_sorted_no_recursion_error(self):
        data = list(range(3000))
        self.assertEqual(deterministic_quicksort(list(data)), data)


class TestHashTable(unittest.TestCase):
    def test_insert_search(self):
        t = HashTable(seed=1)
        t.insert("a", 1)
        t.insert(5, "five")
        self.assertEqual(t.search("a"), 1)
        self.assertEqual(t.search(5), "five")
        self.assertIsNone(t.search("missing"))

    def test_update_existing_key(self):
        t = HashTable(seed=1)
        t.insert("k", 1)
        t.insert("k", 2)
        self.assertEqual(t.search("k"), 2)
        self.assertEqual(len(t), 1)

    def test_delete(self):
        t = HashTable(seed=1)
        t.insert("x", 10)
        self.assertTrue(t.delete("x"))
        self.assertFalse(t.delete("x"))
        self.assertNotIn("x", t)
        self.assertEqual(len(t), 0)

    def test_none_value_is_found(self):
        t = HashTable(seed=1)
        t.insert("n", None)
        self.assertIn("n", t)

    def test_many_keys_against_dict(self):
        rng = random.Random(2)
        t, ref = HashTable(seed=3), {}
        for _ in range(20000):
            k = rng.randint(0, 5000)
            op = rng.random()
            if op < 0.5:
                t.insert(k, k * 2)
                ref[k] = k * 2
            elif op < 0.8:
                self.assertEqual(t.search(k), ref.get(k))
            else:
                self.assertEqual(t.delete(k), ref.pop(k, None) is not None)
        self.assertEqual(len(t), len(ref))

    def test_resizing_keeps_load_factor_bounded(self):
        t = HashTable(capacity=4, seed=4)
        for i in range(10000):
            t.insert(i, i)
            self.assertLessEqual(t.load_factor, t.max_load)
        for i in range(9990):
            t.delete(i)
        self.assertGreaterEqual(t.load_factor, t.min_load)
        for i in range(9990, 10000):
            self.assertEqual(t.search(i), i)


if __name__ == "__main__":
    unittest.main()
