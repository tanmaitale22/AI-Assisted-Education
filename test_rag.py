from rag.chunker import chunk_text
from rag.embeddings import create_embedding
from rag.vector_store import VectorStore


# Sample study material
text = """
Artificial Intelligence is the field of computer science concerned
with creating systems that can perform tasks requiring human intelligence.

Machine Learning is a subset of Artificial Intelligence.
Machine Learning allows computers to learn patterns from data.

Supervised Learning is a type of Machine Learning where the model
learns from labelled training data.

Unsupervised Learning works with data that does not have labelled outputs.
Clustering is a common example of unsupervised learning.

Neural Networks are computational models made up of interconnected
layers of nodes. They are widely used in modern Artificial Intelligence.
"""


# 1. Split text into chunks
chunks = chunk_text(text)

print("\nCHUNKS:")
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i}:")
    print(chunk)


# 2. Create embeddings
embeddings = []

for chunk in chunks:
    embedding = create_embedding(chunk)
    embeddings.append(embedding)

print("\nEmbeddings created:", len(embeddings))


# 3. Store embeddings in FAISS
store = VectorStore()

store.add_chunks(
    chunks,
    embeddings
)

print("Chunks stored in FAISS.")


# 4. Test a question
question = "What is supervised learning?"

query_embedding = create_embedding(question)


# 5. Search FAISS
results = store.search(
    query_embedding,
    top_k=3
)


print("\nRETRIEVED CHUNKS:")

for i, result in enumerate(results):
    print(f"\nResult {i + 1}:")
    print(result)