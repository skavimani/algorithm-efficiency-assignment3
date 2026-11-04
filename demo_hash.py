from hash_table import HashTable

t = HashTable(capacity=4, seed=42)

print("--- Insert ---")
for name, grade in [("alice", 90), ("bob", 85), ("carol", 78), ("dave", 92), ("eve", 88)]:
    t.insert(name, grade)
    print(f"insert({name!r}, {grade})  size={len(t)}  slots={t.capacity}  load factor={t.load_factor:.2f}")

print("\n--- Search ---")
print("search('carol') ->", t.search("carol"))
print("search('zara')  ->", t.search("zara"))

print("\n--- Update existing key ---")
t.insert("bob", 95)
print("search('bob') ->", t.search("bob"))

print("\n--- Delete ---")
print("delete('alice') ->", t.delete("alice"))
print("delete('alice') ->", t.delete("alice"))
print("search('alice') ->", t.search("alice"))

print("\n--- Chains (collisions) ---")
print("chain lengths:", t.chain_lengths())
