import os
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "120"
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

load_dotenv()

QDRANT_HOST = '127.0.0.1'  # Use working host
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
COLLECTION_NAME = 'math_kb'
EMBED_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

router = APIRouter()

client = QdrantClient(
    host=QDRANT_HOST, 
    port=QDRANT_PORT,
    timeout=15  # 15 second timeout
)
model = SentenceTransformer(EMBED_MODEL)

@router.post("/kb_search")
async def kb_search(query: str):
    """Search the knowledge base for a relevant math question."""
    # Import guardrails
    from guardrails import guardrails
    # Validate input with guardrails
    valid, message = guardrails.validate_input(query)
    if not valid:
        return {"result": message}
    
    try:
        query_vec = model.encode(query).tolist()
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec,
            limit=1
        )
        if not search_result:
            return {"result": None, "message": "No relevant question found in KB."}
        payload = search_result[0].payload
        result = {
            "result": {
                "question": payload.get("question"),
                "answer": payload.get("answer"),
                "steps": payload.get("steps"),
                "topic": payload.get("topic"),
                "subtopic": payload.get("subtopic"),
                "difficulty": payload.get("difficulty"),
                "source": payload.get("source")
            },
            "score": search_result[0].score
        }
        
        # Validate output with guardrails
        is_valid, message, filtered_result = guardrails.process_response(result)
        if is_valid:
            return filtered_result
        else:
            raise HTTPException(status_code=400, detail={
                "error": message,
                "route": "blocked",
                "message": "Response was blocked by output guardrails."
            })
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
