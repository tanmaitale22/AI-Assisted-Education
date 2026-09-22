# import pickle
# import faiss
# import numpy as np
# from pathlib import Path

# STORE_DIR = Path("rag_storage")

# INDEX_PATH = STORE_DIR / "faiss.index"
# CHUNKS_PATH = STORE_DIR / "chunks.pkl"


# # -----------------------------
# # Load existing data
# # -----------------------------

# with open(CHUNKS_PATH, "rb") as file:
#     chunks = pickle.load(file)

# index = faiss.read_index(str(INDEX_PATH))

# print("Original chunks:", len(chunks))
# print("FAISS vectors:", index.ntotal)


# # -----------------------------
# # Find unique chunks
# # -----------------------------

# unique_chunks = []
# unique_vectors = []
# seen = set()

# vectors = index.reconstruct_n(0, index.ntotal)

# for i, chunk in enumerate(chunks):

#     key = (
#         chunk.get("content", "").strip(),
#         chunk.get("topic", "").strip(),
#         chunk.get("subtopic", "").strip()
#     )

#     if key in seen:
#         continue

#     seen.add(key)

#     unique_chunks.append(chunk)
#     unique_vectors.append(vectors[i])


# # -----------------------------
# # Rebuild FAISS index
# # -----------------------------

# if unique_vectors:

#     dimension = len(unique_vectors[0])

#     new_index = faiss.IndexFlatL2(dimension)

#     new_index.add(
#         np.array(unique_vectors, dtype="float32")
#     )

# else:
#     new_index = None


# # -----------------------------
# # Save cleaned data
# # -----------------------------

# if new_index is not None:

#     faiss.write_index(
#         new_index,
#         str(INDEX_PATH)
#     )

# with open(CHUNKS_PATH, "wb") as file:

#     pickle.dump(
#         unique_chunks,
#         file
#     )


# print("Cleaned chunks:", len(unique_chunks))
# print("Removed duplicates:", len(chunks) - len(unique_chunks))

# if new_index is not None:
#     print("New FAISS vectors:", new_index.ntotal)

import pickle
import faiss
import numpy as np
from pathlib import Path

from rag.dedup_utils import text_tokens, jaccard_similarity

NEAR_DUPLICATE_THRESHOLD = 0.6

STORE_DIR = Path("rag_storage")

INDEX_PATH = STORE_DIR / "faiss.index"
CHUNKS_PATH = STORE_DIR / "chunks.pkl"


# -----------------------------
# Load existing data
# -----------------------------

with open(CHUNKS_PATH, "rb") as file:
    chunks = pickle.load(file)

index = faiss.read_index(str(INDEX_PATH))

print("Original chunks:", len(chunks))
print("FAISS vectors:", index.ntotal)


# -----------------------------
# Find unique chunks
#
# Two passes:
#   1. Exact (content, topic, subtopic) dedup, same as before.
#   2. Near-duplicate dedup within each (topic, subtopic) group, using
#      word-overlap similarity - this catches chunks that were reworded
#      by the LLM on a re-upload/reprocess of the same material rather
#      than stored verbatim.
# -----------------------------

unique_chunks = []
unique_vectors = []
seen = set()

vectors = index.reconstruct_n(0, index.ntotal)

exact_pass_chunks = []
exact_pass_vectors = []

for i, chunk in enumerate(chunks):

    key = (
        chunk.get("content", "").strip(),
        chunk.get("topic", "").strip(),
        chunk.get("subtopic", "").strip()
    )

    if key in seen:
        continue

    seen.add(key)

    exact_pass_chunks.append(chunk)
    exact_pass_vectors.append(vectors[i])

near_dup_removed = 0
kept_tokens_by_location = {}

for chunk, vector in zip(exact_pass_chunks, exact_pass_vectors):

    topic = chunk.get("topic", "").strip()
    subtopic = chunk.get("subtopic", "").strip()
    content = chunk.get("content", "").strip()

    location = (topic, subtopic)
    location_tokens = kept_tokens_by_location.setdefault(location, [])
    candidate_tokens = text_tokens(content)

    is_near_duplicate = any(
        jaccard_similarity(candidate_tokens, other) >= NEAR_DUPLICATE_THRESHOLD
        for other in location_tokens
    )

    if is_near_duplicate:
        near_dup_removed += 1
        continue

    location_tokens.append(candidate_tokens)

    unique_chunks.append(chunk)
    unique_vectors.append(vector)


# -----------------------------
# Rebuild FAISS index
# -----------------------------

if unique_vectors:

    dimension = len(unique_vectors[0])

    new_index = faiss.IndexFlatL2(dimension)

    new_index.add(
        np.array(unique_vectors, dtype="float32")
    )

else:
    new_index = None


# -----------------------------
# Save cleaned data
# -----------------------------

if new_index is not None:

    faiss.write_index(
        new_index,
        str(INDEX_PATH)
    )

with open(CHUNKS_PATH, "wb") as file:

    pickle.dump(
        unique_chunks,
        file
    )


print("Cleaned chunks:", len(unique_chunks))
print("Removed exact duplicates:", len(chunks) - len(exact_pass_chunks))
print("Removed near-duplicates (reworded):", near_dup_removed)
print("Total removed:", len(chunks) - len(unique_chunks))

if new_index is not None:
    print("New FAISS vectors:", new_index.ntotal)