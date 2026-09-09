from memory.memory_store import MemoryStore
import numpy as np
import faiss
from rag.embeddings import create_embedding


class MemoryEngine:

    def __init__(self):
        self.store = MemoryStore()

        self.index = None
        self.memories = []

        self.load_memories()

    def load_memories(self):

        interactions = self.store.get_all_interactions()

        for interaction in interactions:

            (
                memory_id,
                question,
                answer,
                document,
                topic,
                subtopic,
                timestamp
            ) = interaction

            embedding = create_embedding(question)

            vector = np.array(
                [embedding],
                dtype="float32"
            )

            if self.index is None:
                dimension = vector.shape[1]
                self.index = faiss.IndexFlatL2(dimension)

            self.index.add(vector)

            self.memories.append({
                "id": memory_id,
                "question": question,
                "answer": answer,
                "document": document,
                "topic": topic,
                "subtopic": subtopic,
                "timestamp": timestamp
            })

    def remember(
        self,
        question,
        answer,
        document,
        topic,
        subtopic
    ):

        self.store.save_interaction(
            question,
            answer,
            document,
            topic,
            subtopic
        )

        embedding = create_embedding(question)

        vector = np.array(
            [embedding],
            dtype="float32"
        )

        if self.index is None:
            dimension = vector.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(vector)

        interactions = self.store.get_all_interactions()

        latest = interactions[-1]

        self.memories.append({
            "id": latest[0],
            "question": latest[1],
            "answer": latest[2],
            "document": latest[3],
            "topic": latest[4],
            "subtopic": latest[5],
            "timestamp": latest[6]
        })

    def get_relevant_memories(self, question, top_k=5):

        if not self.memories:
            return []

        question_lower = question.lower()

        recent_keywords = [
            "what did we just discuss",
            "what did we just discussed",
            "what did we just talk about",
            "what were we just discussing",
            "what did we discuss",
            "what did we talk about",
            "remind me what we discussed",
            "remind me what we talked about",
            "what was my last question",
            "what did i just ask",
            "what did i ask just now",
            "after that",
            "before that",
            "earlier",
            "previously",
        ]

        is_recent_question = any(
            keyword in question_lower
            for keyword in recent_keywords
        )

        # Conversation-history questions
        if is_recent_question:

            recent_memories = self.memories[-top_k:]

            # Keep chronological order:
            # oldest → newest
            return recent_memories

        # Normal topic-based memory retrieval
        if self.index is None:
            return []

        query_embedding = create_embedding(question)

        query_vector = np.array(
            [query_embedding],
            dtype="float32"
        )

        k = min(top_k, len(self.memories))

        distances, indices = self.index.search(
            query_vector,
            k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index == -1:
                continue

            print(
                "Memory:",
                self.memories[index]["question"],
                "| Distance:",
                distance
            )

            results.append(
                self.memories[index]
            )

        return results