import faiss
import numpy as np
import pickle
from pathlib import Path


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

        vectors = np.array(
            embeddings,
            dtype="float32"
        )

        dimension = vectors.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(vectors)

        self.chunks.extend(chunks)

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