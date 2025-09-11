#!/usr/bin/env python3
"""
Fixed Knowledge Base Embedding Script
This script will definitely create and populate the math_kb collection
"""

import os
import json
import time
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer

# Configuration
COLLECTION_NAME = 'math_kb'
EMBED_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

def get_qdrant_client():
    """Get working Qdrant client for Windows Docker"""
    hosts = ['host.docker.internal', 'localhost', '127.0.0.1']
    
    for host in hosts:
        try:
            print(f"🔄 Trying connection to {host}:6333...")
            client = QdrantClient(host=host, port=6333, timeout=30)
            # Test connection
            client.get_collections()
            print(f"✅ Connected to Qdrant at {host}:6333")
            return client, host
        except Exception as e:
            print(f"❌ Failed to connect to {host}: {e}")
            continue
    
    raise Exception("Could not connect to Qdrant. Make sure it's running on port 6333")

def create_collection(client):
    """Create or recreate the collection"""
    try:
        # Delete if exists
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"🗑️ Deleted existing collection '{COLLECTION_NAME}'")
            time.sleep(2)
        except:
            pass
        
        # Create new collection
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"✅ Created collection '{COLLECTION_NAME}'")
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        raise

def load_and_validate_data():
    """Load and validate dataset files"""
    datasets = [
        "normalized_math.json",
        "normalized_demo.json", 
        "normalized_jee.json"
    ]
    
    all_data = []
    for dataset in datasets:
        if os.path.exists(dataset):
            print(f"📁 Loading {dataset}...")
            try:
                with open(dataset, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    valid_items = []
                    for item in data:
                        if isinstance(item, dict) and 'question' in item:
                            valid_items.append(item)
                    
                    print(f"✅ Loaded {len(valid_items)} valid items from {dataset}")
                    all_data.extend(valid_items)
                else:
                    print(f"⚠️ {dataset} is not a list, skipping")
                    
            except Exception as e:
                print(f"❌ Error loading {dataset}: {e}")
        else:
            print(f"⚠️ {dataset} not found")
    
    print(f"📊 Total valid items: {len(all_data)}")
    return all_data

def embed_and_upload(client, data, model):
    """Embed and upload data to Qdrant"""
    if not data:
        print("❌ No data to embed!")
        return
    
    print(f"🚀 Starting embedding process for {len(data)} items...")
    
    batch_size = 100
    batch = []
    uploaded_count = 0
    
    for idx, item in enumerate(data):
        try:
            # Get question text
            question = item.get('question', '')
            if not question:
                continue
                
            # Create embedding
            vector = model.encode(question).tolist()
            
            # Create point
            point = PointStruct(
                id=idx,
                vector=vector,
                payload=item
            )
            batch.append(point)
            
            # Upload batch when full
            if len(batch) >= batch_size:
                client.upsert(collection_name=COLLECTION_NAME, points=batch)
                uploaded_count += len(batch)
                print(f"⬆️ Uploaded batch: {uploaded_count}/{len(data)} items")
                batch.clear()
                
        except Exception as e:
            print(f"⚠️ Error processing item {idx}: {e}")
            continue
    
    # Upload remaining items
    if batch:
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        uploaded_count += len(batch)
        print(f"⬆️ Uploaded final batch: {uploaded_count}/{len(data)} items")
    
    print(f"🎉 Successfully uploaded {uploaded_count} vectors!")
    return uploaded_count

def verify_collection(client):
    """Verify the collection was created and populated"""
    try:
        # Simple verification - just try to search
        model = SentenceTransformer(EMBED_MODEL)
        test_vector = model.encode("test query").tolist()
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=test_vector,
            limit=1
        )
        if results:
            print(f"✅ Search test successful - found result with score {results[0].score}")
            print(f"✅ Collection '{COLLECTION_NAME}' is working properly")
            return True
        else:
            print("⚠️ Search test failed - no results")
            return False
        
    except Exception as e:
        if "doesn't exist" in str(e):
            print(f"❌ Collection '{COLLECTION_NAME}' doesn't exist")
            return False
        else:
            print(f"⚠️ Error during verification (but may still work): {e}")
            # Try a simple search anyway
            try:
                model = SentenceTransformer(EMBED_MODEL)
                test_vector = model.encode("what is 2+2").tolist()
                results = client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=test_vector,
                    limit=1
                )
                if results:
                    print(f"✅ Despite error, search works! Found result with score {results[0].score}")
                    return True
            except:
                pass
            return False

def main():
    print("🚀 Starting Knowledge Base Fix...")
    
    try:
        # Connect to Qdrant
        client, host = get_qdrant_client()
        
        # Load embedding model
        print("📥 Loading embedding model...")
        model = SentenceTransformer(EMBED_MODEL)
        
        # Create collection
        create_collection(client)
        
        # Load data
        data = load_and_validate_data()
        if not data:
            print("❌ No valid data found!")
            return False
        
        # Embed and upload
        uploaded = embed_and_upload(client, data, model)
        
        # Verify
        success = verify_collection(client)
        
        if success:
            print("🎉 Knowledge Base is now working!")
            print(f"📍 Connected to: {host}:6333")
            print(f"📊 Collection: {COLLECTION_NAME}")
            print(f"🔢 Vectors: {uploaded}")
            return True
        else:
            print("❌ Knowledge Base setup failed!")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ KB is ready! You can now restart your FastAPI server.")
    else:
        print("\n❌ KB setup failed. Check the errors above.")
