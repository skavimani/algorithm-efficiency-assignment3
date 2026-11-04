"""
Hash table with separate chaining and a universal hash function.

Hash function (Carter & Wegman, 1979):

    h_{a,b}(k) = ((a * k + b) mod p) mod m

where p = 2**61 - 1 (a Mersenne prime larger than any key we hash),
a is chosen at random from {1, ..., p-1} and b from {0, ..., p-1}.
Choosing (a, b) at random when the table is created means that, for any two
distinct keys, the probability they collide is at most about 1/m, no matter
which keys an adversary picks.

Non-integer keys (strings, tuples, ...) are first turned into an integer
with a polynomial "pre-hash" and then fed to h_{a,b}.

Each slot holds a Python list (the "chain") of [key, value] pairs.

Dynamic resizing keeps the load factor alpha = n / m in a fixed band:
    * grow  (double m) when alpha would exceed MAX_LOAD (default 1.0)
    * shrink (halve m) when alpha drops below MIN_LOAD (default 0.25)
A new (a, b) pair is drawn on every resize.
"""

import random

_P = (1 << 61) - 1  # Mersenne prime 2^61 - 1


def _prehash(key):
    """Map any hashable key to a non-negative integer."""
    if isinstance(key, bool):
        return int(key)
    if isinstance(key, int):
        return key % _P
    if isinstance(key, str):
        h = 0
        for ch in key:
            h = (h * 131 + ord(ch)) % _P
        return h
    # Fallback for other hashable types (tuples, floats, ...)
    return hash(key) % _P


class HashTable:
    def __init__(self, capacity=8, max_load=1.0, min_load=0.25,
                 resize=True, seed=None):
        self._rng = random.Random(seed)
        self._m = max(1, capacity)
        self._min_capacity = self._m
        self._buckets = [[] for _ in range(self._m)]
        self._n = 0
        self.max_load = max_load
        self.min_load = min_load
        self.resize_enabled = resize
        self._new_hash_function()

    # ---------- hashing ----------
    def _new_hash_function(self):
        self._a = self._rng.randint(1, _P - 1)
        self._b = self._rng.randint(0, _P - 1)

    def _index(self, key):
        k = _prehash(key)
        return ((self._a * k + self._b) % _P) % self._m

    # ---------- public operations ----------
    def insert(self, key, value):
        """Add key -> value. If key already exists its value is replaced."""
        chain = self._buckets[self._index(key)]
        for pair in chain:
            if pair[0] == key:
                pair[1] = value
                return
        chain.append([key, value])
        self._n += 1
        if self.resize_enabled and self._n / self._m > self.max_load:
            self._rehash(self._m * 2)

    def search(self, key, default=None):
        """Return the value stored for key, or default if absent."""
        for k, v in self._buckets[self._index(key)]:
            if k == key:
                return v
        return default

    def delete(self, key):
        """Remove key. Returns True if it was present, False otherwise."""
        chain = self._buckets[self._index(key)]
        for i, pair in enumerate(chain):
            if pair[0] == key:
                chain[i] = chain[-1]  # O(1) removal: swap with last, pop
                chain.pop()
                self._n -= 1
                if (self.resize_enabled and self._m > self._min_capacity
                        and self._n / self._m < self.min_load):
                    self._rehash(max(self._min_capacity, self._m // 2))
                return True
        return False

    # ---------- resizing ----------
    def _rehash(self, new_m):
        old_items = [pair for chain in self._buckets for pair in chain]
        self._m = new_m
        self._buckets = [[] for _ in range(self._m)]
        self._new_hash_function()
        for key, value in old_items:
            self._buckets[self._index(key)].append([key, value])

    # ---------- helpers / statistics ----------
    def __len__(self):
        return self._n

    def __contains__(self, key):
        sentinel = object()
        return self.search(key, sentinel) is not sentinel

    @property
    def capacity(self):
        return self._m

    @property
    def load_factor(self):
        return self._n / self._m

    def chain_lengths(self):
        return [len(c) for c in self._buckets]

    def longest_chain(self):
        return max(self.chain_lengths())


if __name__ == "__main__":
    t = HashTable(seed=1)
    for word in ["apple", "banana", "cherry", "date", "elderberry"]:
        t.insert(word, len(word))
    print("search('cherry') ->", t.search("cherry"))
    print("delete('banana') ->", t.delete("banana"))
    print("search('banana') ->", t.search("banana"))
    print("size:", len(t), " slots:", t.capacity,
          " load factor:", round(t.load_factor, 3))
