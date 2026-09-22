# import faiss
# import numpy as np
# import pickle
# from pathlib import Path


# class VectorStore:

#     def __init__(self):

#         self.index = None
#         self.chunks = []

#         self.store_dir = Path("rag_storage")
#         self.store_dir.mkdir(exist_ok=True)

#         self.index_path = self.store_dir / "faiss.index"
#         self.chunks_path = self.store_dir / "chunks.pkl"

#         self.load()

#     # --------------------------------
#     # Add chunks
#     # --------------------------------

#     def add_chunks(self, chunks, embeddings):

#         if not chunks:
#             return

#         # Create a set of chunks that already exist
#         existing = set()

#         for chunk in self.chunks:
#             key = (
#                 chunk.get("content", "").strip(),
#                 chunk.get("topic", "").strip(),
#                 chunk.get("subtopic", "").strip()
#             )
#             existing.add(key)

#         new_chunks = []
#         new_embeddings = []

#         # Keep only chunks that are not already stored
#         for chunk, embedding in zip(chunks, embeddings):

#             key = (
#                 chunk.get("content", "").strip(),
#                 chunk.get("topic", "").strip(),
#                 chunk.get("subtopic", "").strip()
#             )

#             if key in existing:
#                 continue

#             existing.add(key)

#             new_chunks.append(chunk)
#             new_embeddings.append(embedding)

#         # Nothing new to add
#         if not new_chunks:
#             return

#         vectors = np.array(
#             new_embeddings,
#             dtype="float32"
#         )

#         dimension = vectors.shape[1]

#         if self.index is None:
#             self.index = faiss.IndexFlatL2(dimension)

#         self.index.add(vectors)

#         self.chunks.extend(new_chunks)

#         self.save()

#     # --------------------------------
#     # Save vector store
#     # --------------------------------

#     def save(self):

#         if self.index is not None:
#             faiss.write_index(
#                 self.index,
#                 str(self.index_path)
#             )

#         with open(self.chunks_path, "wb") as file:
#             pickle.dump(
#                 self.chunks,
#                 file
#             )

#     # --------------------------------
#     # Load vector store
#     # --------------------------------

#     def load(self):

#         if self.index_path.exists():
#             self.index = faiss.read_index(
#                 str(self.index_path)
#             )

#         if self.chunks_path.exists():
#             with open(self.chunks_path, "rb") as file:
#                 self.chunks = pickle.load(file)

#     # --------------------------------
#     # Semantic search
#     # --------------------------------

#     def search(self, query_embedding, top_k=3):

#         if self.index is None or not self.chunks:
#             return []

#         query_vector = np.array(
#             [query_embedding],
#             dtype="float32"
#         )

#         k = min(
#             top_k,
#             len(self.chunks)
#         )

#         distances, indices = self.index.search(
#             query_vector,
#             k
#         )

#         results = []

#         for index in indices[0]:

#             if index != -1:
#                 results.append(
#                     self.chunks[index]
#                 )

#         return results

#     # --------------------------------
#     # Search by topic/subtopic
#     # --------------------------------

#     def search_by_location(
#         self,
#         topic=None,
#         subtopic=None
#     ):

#         results = []

#         for chunk in self.chunks:

#             if topic and chunk.get("topic") != topic:
#                 continue

#             if subtopic and chunk.get("subtopic") != subtopic:
#                 continue

#             results.append(chunk)

#         return results

import faiss
import numpy as np
import pickle
from pathlib import Path

from rag.dedup_utils import text_tokens, jaccard_similarity

NEAR_DUPLICATE_THRESHOLD = 0.6


class VectorStore:

    def __init__(self):

        self.index = None
        self.chunks = []

        self.store_dir = Path("rag_storage")
        self.store_dir.mkdir(exist_ok=True)

        self.index_path = self.store_dir / "faiss.index"
        self.chunks_path = self.store_dir / "chunks.pkl"

        self.load()

    # --------------------------------
    # Add chunks
    # --------------------------------

    def add_chunks(self, chunks, embeddings):

        if not chunks:
            return

        # Create a set of chunks that already exist (exact-text dedup)
        existing = set()

        # Word-overlap tokens of existing chunks, grouped by
        # (topic, subtopic), so we can also catch chunks that were
        # *reworded* rather than stored verbatim (e.g. the same concept
        # regenerated by the LLM on a re-upload/reprocess).
        existing_tokens_by_location = {}

        for chunk in self.chunks:
            topic = chunk.get("topic", "").strip()
            subtopic = chunk.get("subtopic", "").strip()
            content = chunk.get("content", "").strip()

            key = (content, topic, subtopic)
            existing.add(key)

            location = (topic, subtopic)
            existing_tokens_by_location.setdefault(location, []).append(
                text_tokens(content)
            )

        new_chunks = []
        new_embeddings = []

        # Keep only chunks that are not already stored, either verbatim
        # or as a near-duplicate (same topic/subtopic, highly overlapping
        # wording) of something already stored or already queued in this
        # same batch.
        for chunk, embedding in zip(chunks, embeddings):

            topic = chunk.get("topic", "").strip()
            subtopic = chunk.get("subtopic", "").strip()
            content = chunk.get("content", "").strip()

            key = (content, topic, subtopic)

            if key in existing:
                continue

            location = (topic, subtopic)
            location_tokens = existing_tokens_by_location.setdefault(location, [])
            candidate_tokens = text_tokens(content)

            is_near_duplicate = any(
                jaccard_similarity(candidate_tokens, other) >= NEAR_DUPLICATE_THRESHOLD
                for other in location_tokens
            )

            if is_near_duplicate:
                continue

            existing.add(key)
            location_tokens.append(candidate_tokens)

            new_chunks.append(chunk)
            new_embeddings.append(embedding)

        # Nothing new to add
        if not new_chunks:
            return

        vectors = np.array(
            new_embeddings,
            dtype="float32"
        )

        dimension = vectors.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(vectors)

        self.chunks.extend(new_chunks)

        self.save()

    # --------------------------------
    # Save vector store
    # --------------------------------

    def save(self):

        if self.index is not None:
            faiss.write_index(
                self.index,
                str(self.index_path)
            )

        with open(self.chunks_path, "wb") as file:
            pickle.dump(
                self.chunks,
                file
            )

    # --------------------------------
    # Load vector store
    # --------------------------------

    def load(self):

        if self.index_path.exists():
            self.index = faiss.read_index(
                str(self.index_path)
            )

        if self.chunks_path.exists():
            with open(self.chunks_path, "rb") as file:
                self.chunks = pickle.load(file)

    # --------------------------------
    # Semantic search
    # --------------------------------

    def search(self, query_embedding, top_k=3):

        if self.index is None or not self.chunks:
            return []

        query_vector = np.array(
            [query_embedding],
            dtype="float32"
        )

        k = min(
            top_k,
            len(self.chunks)
        )

        distances, indices = self.index.search(
            query_vector,
            k
        )

        results = []

        for index in indices[0]:

            if index != -1:
                results.append(
                    self.chunks[index]
                )

        return results

    # --------------------------------
    # Search by topic/subtopic
    # --------------------------------

    def search_by_location(
        self,
        topic=None,
        subtopic=None
    ):

        results = []

        for chunk in self.chunks:

            if topic and chunk.get("topic") != topic:
                continue

            if subtopic and chunk.get("subtopic") != subtopic:
                continue

            results.append(chunk)

        return results