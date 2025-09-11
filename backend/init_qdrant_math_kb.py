# This script creates the 'math_kb' collection in Qdrant and uploads sample data.
# Run this script after Qdrant is running.

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, PointStruct
import numpy as np

# Connect to Qdrant (default local Docker)
client = QdrantClient(host="localhost", port=6333)

# Create the collection if it doesn't exist
collection_name = "math_kb"
vector_size = 8  # Example size, adjust to your embedding size

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_size, distance="Cosine")
)

# Upload some sample points (replace with your real data/embeddings)
sample_texts = [
    "What is the Pythagorean theorem?",
    "Explain the quadratic formula.",
    "What is a prime number?"
]

for idx, text in enumerate(sample_texts):
    # Dummy vector, replace with your embedding model output
    vector = np.random.rand(vector_size).tolist()
    point = PointStruct(
        id=idx,
        vector=vector,
        payload={"text": text}
    )
    client.upsert(collection_name=collection_name, points=[point])

print(f"Collection '{collection_name}' created and sample data uploaded.")
