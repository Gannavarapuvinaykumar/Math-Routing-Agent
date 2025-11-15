from __future__ import annotations
import sys, os
# Import client
try:
    from backend.agent_pipeline import client, COLLECTION_NAME
except Exception:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from agent_pipeline import client, COLLECTION_NAME

print('Collection:', COLLECTION_NAME)
try:
    resp = client.scroll(collection_name=COLLECTION_NAME, limit=20, with_payload=True)
    points = getattr(resp, 'points', None) or resp
    for i, pt in enumerate(points[:20]):
        pid = getattr(pt, 'id', None) or (pt.get('id') if isinstance(pt, dict) else None)
        payload = getattr(pt, 'payload', None) or (pt.get('payload') if isinstance(pt, dict) else None)
        print('--- Point', i, 'id=', pid)
        print(payload)
except Exception as e:
    print('Error fetching points:', e)
