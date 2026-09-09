from rag.embeddings import create_embedding
from rag.vector_store import VectorStore


class RAGEngine:

    def __init__(self):
        self.vector_store = VectorStore()

    def add_document(self, chunks):

        embeddings = []

        for chunk in chunks:
            embedding = create_embedding(
                chunk["content"]
            )

            embeddings.append(embedding)

        self.vector_store.add_chunks(
            chunks,
            embeddings
        )

        return chunks

    def retrieve(self, question, top_k=3, topic=None, subtopic=None):

        # If the student selected a specific subtopic,
        # retrieve directly from that location.
        if topic or subtopic:

            results = self.vector_store.search_by_location(
                topic=topic,
                subtopic=subtopic
            )

            if results:
                return results[:top_k]

        # Otherwise fall back to normal semantic search.
        question_embedding = create_embedding(question)

        results = self.vector_store.search(
            question_embedding,
            top_k=top_k
        )

        return results