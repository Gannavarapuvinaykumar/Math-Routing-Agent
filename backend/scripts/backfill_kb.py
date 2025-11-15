"""
Backfill script for math_kb collection.
- Adds `question_norm` to each point payload (normalized question text).
- Optionally recomputes question-only vectors to match current embedding policy.
- Upserts updated points back into Qdrant (non-destructive).

Usage (from repo root):
    python backend\scripts\backfill_kb.py

"""
from __future__ import annotations
import sys
import time
from typing import Any, Dict, List

# Import app's client and model
try:
    # Try importing as a package first (when running from repo root)
    try:
        from backend.agent_pipeline import client, model, COLLECTION_NAME
    except Exception:
        # Running from backend/scripts folder; ensure parent backend/ is on sys.path
        import os, sys
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from agent_pipeline import client, model, COLLECTION_NAME
except Exception as e:
    print("Failed to import agent_pipeline (ensure you're running from the repo root or backend folder):", e)
    raise

BATCH_SIZE = 100
RECOMPUTE_VECTORS = True  # Set to False if you only want to add question_norm


def normalize_question(q: str) -> str:
    return " ".join(q.strip().lower().split()) if q else ""


def extract_point_fields(pt: Any) -> Dict[str, Any]:
    """Return a dict with id, payload, vector for a point-like object or dict."""
    # Support both dict-like and object-like shapes returned by Qdrant
    pid = None
    payload = None
    vector = None

    # Try dict access first
    if isinstance(pt, dict):
        pid = pt.get("id")
        payload = pt.get("payload") or {}
        vector = pt.get("vector")
    else:
        # object-like
        pid = getattr(pt, "id", None) or (pt.payload.get("id") if getattr(pt, "payload", None) else None)
        payload = getattr(pt, "payload", None) or {}
        vector = getattr(pt, "vector", None)

    return {"id": pid, "payload": payload, "vector": vector}


def run_backfill():
    print("Starting backfill for collection:", COLLECTION_NAME)

    updated = 0
    skipped = 0
    total = 0
    batch: List[Dict[str, Any]] = []

    try:
        # Use scroll to iterate all points
        print("Fetching points via scroll...")
        offset = None
        while True:
            # Qdrant's python client supports scroll with 'offset' or 'next_page' depending on version.
            try:
                if offset is None:
                    resp = client.scroll(collection_name=COLLECTION_NAME, limit=BATCH_SIZE, with_payload=True)
                else:
                    resp = client.scroll(collection_name=COLLECTION_NAME, limit=BATCH_SIZE, with_payload=True, offset=offset)
            except TypeError:
                # Older/newer client signature differences: try without offset
                resp = client.scroll(collection_name=COLLECTION_NAME, limit=BATCH_SIZE, with_payload=True, with_vector=True)

            points = getattr(resp, "points", None) or resp
            if not points:
                break

            for pt in points:
                total += 1
                fields = extract_point_fields(pt)
                pid = fields["id"]
                payload = fields["payload"] or {}
                question = payload.get("question")

                if not question:
                    skipped += 1
                    continue

                question_norm = normalize_question(question)
                needs_update = False

                if payload.get("question_norm") != question_norm:
                    payload["question_norm"] = question_norm
                    needs_update = True

                new_vector = None
                if RECOMPUTE_VECTORS:
                    try:
                        new_vector = model.encode(question).tolist()
                        # Compare lengths as a cheap check if vector differs; always update vector to be safe
                        if fields.get("vector") != new_vector:
                            needs_update = True
                    except Exception as e:
                        print(f"Failed to compute vector for id={pid}: {e}")

                if needs_update:
                    point = {"id": pid or int(time.time() * 1000), "vector": new_vector if new_vector is not None else fields.get("vector"), "payload": payload}
                    batch.append(point)

                if len(batch) >= BATCH_SIZE:
                    client.upsert(collection_name=COLLECTION_NAME, points=batch)
                    updated += len(batch)
                    print(f"Upserted batch of {len(batch)} points (total updated: {updated})")
                    batch = []

            # If resp supports next_page_token, use it; else break if fewer than limit returned
            if hasattr(resp, "next_page_token") and getattr(resp, "next_page_token"):
                offset = getattr(resp, "next_page_token")
            else:
                # If we received fewer than the batch limit, we've reached the end
                if len(points) < BATCH_SIZE:
                    break
                # Otherwise continue and rely on offsetless scroll
                # To avoid infinite loops, break — most clients will return empty at the end
                break

        if batch:
            client.upsert(collection_name=COLLECTION_NAME, points=batch)
            updated += len(batch)
            print(f"Upserted final batch of {len(batch)} points")

        print("Backfill complete. Total points scanned:", total)
        print("Points updated:", updated)
        print("Points skipped (no question field):", skipped)

    except Exception as e:
        print("Backfill failed:", e)
        raise


if __name__ == "__main__":
    run_backfill()
