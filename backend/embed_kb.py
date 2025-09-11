# Math Routing Agent: Embedding Script with Batching
# This script embeds math questions and uploads them to Qdrant in safe chunks.

import os
import json
import time
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer

QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
COLLECTION_NAME = 'math_kb'

# Use a compact math-friendly embedding model
EMBED_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Initialize Qdrant client with better error handling for Windows Docker
def get_qdrant_client():
    """Get Qdrant client with retry logic and Windows Docker support"""
    max_retries = 5
    hosts_to_try = [
        QDRANT_HOST,
        'localhost',
        '127.0.0.1',
        'host.docker.internal'  # Windows Docker specific
    ]
    
    for host in hosts_to_try:
        for attempt in range(max_retries):
            try:
                print(f"🔄 Trying connection to {host}:{QDRANT_PORT} (attempt {attempt + 1})")
                client = QdrantClient(
                    host=host,
                    port=QDRANT_PORT,
                    timeout=30  # Reasonable timeout
                )
                # Test connection
                collections = client.get_collections()
                print(f"✅ Successfully connected to Qdrant at {host}:{QDRANT_PORT}")
                return client
            except Exception as e:
                print(f"⚠️ Connection to {host} attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    continue
    
    raise Exception("Could not connect to Qdrant after trying all hosts and retries")

client = None
model = SentenceTransformer(EMBED_MODEL)


def create_collection():
    """Create or reset the Qdrant collection."""
    global client
    try:
        print(f"🔍 Checking connection to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
        
        # Initialize client with retry logic
        if client is None:
            client = get_qdrant_client()

        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME in collection_names:
            print(f"🗑️ Deleting existing collection '{COLLECTION_NAME}'...")
            client.delete_collection(COLLECTION_NAME)
            time.sleep(2)  # Wait for deletion to complete

        print(f"🆕 Creating new collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        time.sleep(2)  # Wait for creation to complete
        print(f"✅ Collection '{COLLECTION_NAME}' created successfully!")

    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        print("💡 Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant:latest")
        raise


def embed_and_upload(json_path, batch_size=500):
    """Embed and upload data in safe batches."""
    try:
        print(f"📖 Loading data from {json_path}...")

        if not os.path.exists(json_path):
            print(f"⚠️ File {json_path} not found, skipping...")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"🔢 Processing {len(data)} items...")

        batch = []
        for idx, item in enumerate(data):
            if "question" not in item:
                print(f"⚠️ Skipping item {idx}: missing 'question' field")
                continue

            try:
                vec = model.encode(item["question"])
                batch.append(
                    PointStruct(id=idx, vector=vec.tolist(), payload=item)
                )
            except Exception as e:
                print(f"⚠️ Error embedding item {idx}: {e}")
                continue

            # Upload in batches
            if len(batch) >= batch_size:
                print(f"⬆️ Uploading batch of {len(batch)} vectors...")
                client.upsert(collection_name=COLLECTION_NAME, points=batch)
                batch.clear()

            if (idx + 1) % 1000 == 0:
                print(f"✅ Processed {idx + 1}/{len(data)} items")

        # Upload remaining vectors
        if batch:
            print(f"⬆️ Uploading final batch of {len(batch)} vectors...")
            client.upsert(collection_name=COLLECTION_NAME, points=batch)

        print(f"🎉 Finished uploading {len(data)} vectors from {json_path}")

    except Exception as e:
        print(f"❌ Error processing {json_path}: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Starting Math Knowledge Base Embedding Process...")

    try:
        # Create/reset collection
        create_collection()
        time.sleep(2)

        datasets = [
            "normalized_demo.json",
            "normalized_jee.json",
            "normalized_math.json"
        ]

        total_processed = 0
        for dataset in datasets:
            print(f"\n📁 Processing dataset: {dataset}")
            if os.path.exists(dataset):
                embed_and_upload(dataset, batch_size=500)
                total_processed += 1
            else:
                print(f"⚠️ Dataset {dataset} not found, skipping...")

        print(f"\n🎉 Embedding process completed!")
        print(f"📊 Processed {total_processed} dataset(s)")

        # Verify collection
        info = client.get_collection(COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' now contains {info.points_count} vectors")

    except Exception as e:
        print(f"\n❌ Embedding process failed: {e}")
        exit(1)
