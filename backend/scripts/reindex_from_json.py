"""
Reindex KB from `normalized_math.json` into Qdrant `math_kb` collection.
- Non-destructive: creates collection only if missing.
- Upserts points with payloads and question_norm, computes question-only vectors using current embedding model.

Usage (from backend/ working dir):
    .venv\Scripts\python.exe scripts\reindex_from_json.py
"""
import json
import os
import sys
import time

try:
    from backend.agent_pipeline import client, model, COLLECTION_NAME
except Exception:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from agent_pipeline import client, model, COLLECTION_NAME

INPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'normalized_math.json')
BATCH_SIZE = 100


def normalize_question(q: str) -> str:
    return " ".join(q.strip().lower().split()) if q else ""


def ensure_collection(vec_size: int):
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        print(f"Creating collection '{COLLECTION_NAME}' with vector size {vec_size}")
        from qdrant_client.http.models import VectorParams
        client.create_collection(collection_name=COLLECTION_NAME, vectors_config=VectorParams(size=vec_size, distance="Cosine"))
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists; will upsert into it (non-destructive)")


def run_reindex():
    print("Reading data from:", INPUT_FILE)
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} entries")

    batch = []
    updated = 0
    for entry in data:
        question = entry.get('question')
        answer = entry.get('answer')
        steps = entry.get('steps')
        metadata = {
            'topic': entry.get('topic'),
            'subtopic': entry.get('subtopic'),
            'difficulty': entry.get('difficulty')
        }
        qid = entry.get('id') or int(time.time() * 1000)
        qnorm = normalize_question(question)

        # Compute vector
        try:
            vec = model.encode(question).tolist()
        except Exception as e:
            print(f"Failed to embed question '{question}': {e}")
            continue

        payload = {
            'question': question,
            'question_norm': qnorm,
            'answer': answer,
            'steps': steps,
            'topic': metadata.get('topic'),
            'subtopic': metadata.get('subtopic'),
            'difficulty': metadata.get('difficulty'),
            'source': entry.get('source', 'dataset'),
            'route_origin': entry.get('source', 'dataset'),
            'validated_by_user': False,
            'created_at': entry.get('created_at') or None,
            'additional_sources': entry.get('sources') or []
        }

        point = {
            'id': qid,
            'vector': vec,
            'payload': payload
        }

        batch.append(point)
        if len(batch) >= BATCH_SIZE:
            # Ensure collection exists before first upsert
            ensure_collection(len(vec))
            client.upsert(collection_name=COLLECTION_NAME, points=batch)
            updated += len(batch)
            print(f"Upserted batch of {len(batch)} (total {updated})")
            batch = []

    if batch:
        ensure_collection(len(batch[0]['vector']))
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        updated += len(batch)
        print(f"Upserted final batch of {len(batch)}")

    print("Reindex complete. Total upserted:", updated)


if __name__ == '__main__':
    run_reindex()
