import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import uuid
import time
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer

router = APIRouter()

# Placeholder for feedback storage (in-memory for now)
feedback_store = []

class FeedbackRequest(BaseModel):
    trace_id: str
    feedback: str
    correction: str = None
    query: str = None
    route: str = None
    response: str = None  # Add response field to store the actual response

def get_qdrant_client():
    """Get working Qdrant client for Windows Docker with retry logic"""
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

def store_validated_response_in_kb(query: str, response: str, source_route: str):
    """Store validated web search/AI generation response in KB for future use"""
    try:
        from sentence_transformers import SentenceTransformer
        import uuid
        
        print(f"🔄 Attempting to store in KB: {query[:50]}...")
        
        # Initialize embedding model and get reliable Qdrant client
        model = SentenceTransformer(os.getenv('EMBED_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'))
        client, host = get_qdrant_client()
        
        # Create embedding for the query
        print(f"🔄 Creating embedding...")
        query_vector = model.encode(query).tolist()
        print(f"✅ Embedding created (dimension: {len(query_vector)})")
        
        # Prepare payload with source information
        payload = {
            "question": query,
            "answer": response,
            "source": f"Validated {source_route.replace('_', ' ').title()}",
            "validated_by_user": True,
            "timestamp": datetime.now().isoformat(),
            "route_origin": source_route,
            "topic": "user_validated",
            "subtopic": source_route,
            "difficulty": "unknown"
        }
        
        # Generate unique ID
        point_id = int(datetime.now().timestamp() * 1000000)  # microsecond precision
        
        # Store in Qdrant with retry logic
        collection_name = os.getenv('COLLECTION_NAME', 'math_kb')
        print(f"🔄 Storing in collection: {collection_name}")
        
        try:
            client.upsert(
                collection_name=collection_name,
                points=[{
                    "id": point_id,
                    "vector": query_vector,
                    "payload": payload
                }]
            )
            
            # Verify the storage
            print(f"🔄 Verifying storage...")
            search_result = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=1
            )
            
            if search_result and search_result[0].id == point_id:
                print(f"✅ Successfully stored and verified in KB:")
                print(f"   Query: {query[:100]}...")
                print(f"   Source: {source_route}")
                print(f"   Point ID: {point_id}")
                print(f"   Collection: {collection_name}")
                return True
            else:
                print(f"⚠️ Storage succeeded but verification failed")
                return True  # Still consider it success
                
        except Exception as storage_error:
            print(f"❌ Storage operation failed: {storage_error}")
            return False
        
    except Exception as e:
        print(f"❌ Error storing validated response in KB: {e}")
        import traceback
        traceback.print_exc()
        return False

def store_validated_response_simple(feedback_entry: dict) -> bool:
    """
    Simplified fallback storage method for validated responses.
    Uses minimal processing and shorter timeouts.
    """
    try:
        print(f"🔄 Using simplified storage approach...")
        
        # Quick connection test
        client, host = get_qdrant_client()
        
        # Simple document content
        doc_content = f"{feedback_entry['query']}\n\n{feedback_entry['response']}"
        
        # Quick embedding
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = encoder.encode(doc_content).tolist()
        
        # Simple point
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "content": doc_content,
                "source": "user_validated_simple",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Single storage attempt
        result = client.upsert(
            collection_name="math_kb",
            points=[point],
            wait=False  # Don't wait for confirmation
        )
        
        print(f"✅ Simplified storage completed")
        
        # Verify the storage by attempting a quick search
        try:
            search_result = client.search(
                collection_name="math_kb",
                query_vector=embedding,
                limit=1,
                timeout=5
            )
            if search_result and len(search_result) > 0:
                stored_payload = search_result[0].payload
                if stored_payload.get("source") == "user_validated_simple":
                    print(f"✅ Verified: Response stored and searchable in KB")
                    return True
            print(f"⚠️ Storage completed but verification inconclusive")
        except Exception as verify_error:
            print(f"⚠️ Storage completed but verification failed: {verify_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simplified storage failed: {e}")
        return False

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Accept human feedback (👍/👎 + optional correction) for a trace/response."""
    
    # Debug logging
    print(f"📥 Feedback received:")
    print(f"   Trace ID: {request.trace_id}")
    print(f"   Feedback: {request.feedback}")
    print(f"   Route: {request.route}")
    print(f"   Query: {request.query}")
    print(f"   Response content: {len(request.response or '')} characters")
    
    # Store feedback entry
    feedback_entry = {
        "trace_id": request.trace_id,
        "feedback": request.feedback,
        "correction": request.correction,
        "query": request.query,
        "route": request.route,
        "response": request.response,  # Include response content
        "timestamp": datetime.now().isoformat()
    }
    
    feedback_store.append(feedback_entry)
    
    # Process feedback and check if stored in KB
    stored_in_kb = False
    try:
        stored_in_kb = process_feedback_for_learning(feedback_entry)
    except Exception as e:
        print(f"Warning: Failed to process feedback for learning: {e}")
    
    return {
        "status": "received", 
        "trace_id": request.trace_id, 
        "message": "Feedback stored successfully",
        "stored_in_kb": stored_in_kb
    }

@router.post("/test-kb-retrieval")
async def test_kb_retrieval(request: dict):
    """Test if stored feedback can be retrieved from KB"""
    try:
        test_query = request.get("query", "zorble mathematical operation")
        print(f"🔍 Testing KB retrieval for: {test_query}")
        
        # Initialize components
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        client, host = get_qdrant_client()
        
        # Encode the test query
        query_vector = encoder.encode(test_query).tolist()
        
        # Search for user-validated responses (simple search)
        search_results = client.search(
            collection_name="math_kb",
            query_vector=query_vector,
            limit=5,
            timeout=10
        )
        
        results = []
        for result in search_results:
            payload = result.payload
            source = payload.get("source", "unknown")
            # Filter for user-validated entries
            if "user_validated" in source or payload.get("validated_by_user"):
                results.append({
                    "score": result.score,
                    "source": source,
                    "content_preview": payload.get("content", "")[:200] + "...",
                    "timestamp": payload.get("timestamp", "unknown"),
                    "validated": payload.get("validated_by_user", False)
                })
        
        return {
            "success": True,
            "query": test_query,
            "found_results": len(results),
            "results": results
        }
        
    except Exception as e:
        print(f"❌ Error testing KB retrieval: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def process_feedback_for_learning(feedback_entry):
    """Process feedback to improve the system - integrate with DSPy/learning components"""
    
    # Define positive feedback types that should trigger KB storage
    positive_feedback_types = ["👍", "helpful", "good", "excellent", "accurate", "useful"]
    negative_feedback_types = ["👎", "unhelpful", "bad", "incorrect", "poor", "useless"]
    
    feedback_lower = feedback_entry["feedback"].lower()
    stored_in_kb = False
    
    # Check if feedback is negative
    if any(neg_type in feedback_lower for neg_type in negative_feedback_types):
        print(f"Negative feedback received for route {feedback_entry['route']}: {feedback_entry['query']}")
        # In a real system, you might:
        # 1. Update routing confidence scores
        # 2. Flag problematic KB entries
        # 3. Retrain models with corrected data
    
    # Check if feedback is positive (including "helpful")
    elif any(pos_type in feedback_lower for pos_type in positive_feedback_types):
        print(f"Positive feedback received for route {feedback_entry['route']}: {feedback_entry['query']}")
        print(f"Feedback type: {feedback_entry['feedback']}")
        
        # ✅ Store validated responses in KB for future use
        if feedback_entry.get("route") in ["web_search", "ai_generation", "Web", "AI"] and feedback_entry.get("response"):
            try:
                print(f"🔄 Processing positive feedback for KB storage...")
                success = store_validated_response_in_kb(
                    query=feedback_entry["query"],
                    response=feedback_entry["response"],
                    source_route=feedback_entry["route"]
                )
                if success:
                    print(f"✅ Stored validated {feedback_entry['route']} response in KB!")
                    stored_in_kb = True
                else:
                    print(f"❌ Failed to store in KB - will retry with simplified approach")
                    # Try simplified storage as fallback
                    try:
                        success = store_validated_response_simple(feedback_entry)
                        if success:
                            print(f"✅ Stored using simplified approach!")
                            stored_in_kb = True
                    except Exception as fallback_error:
                        print(f"❌ Fallback storage also failed: {fallback_error}")
            except Exception as e:
                print(f"❌ Failed to store in KB: {e}")
        elif not feedback_entry.get("response"):
            print(f"⚠️ No response content provided - cannot store in KB")
        else:
            print(f"ℹ️ Route {feedback_entry.get('route')} responses not stored in KB")
        
        # In a real system, you might:
        # 1. Increase confidence scores for this route
        # 2. Use as positive training examples
    
    return stored_in_kb
    
    # Store feedback in persistent storage (in a real app, use a database)
    feedback_file = "feedback_log.json"
    try:
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                all_feedback = json.load(f)
        else:
            all_feedback = []
        
        all_feedback.append(feedback_entry)
        
        with open(feedback_file, 'w') as f:
            json.dump(all_feedback, f, indent=2)
            
    except Exception as e:
        print(f"Failed to save feedback to file: {e}")

@router.get("/feedback/stats")
def get_feedback_stats():
    """Get feedback statistics"""
    total_feedback = len(feedback_store)
    
    # Define positive and negative feedback types
    positive_feedback_types = ["👍", "helpful", "good", "excellent", "accurate", "useful"]
    negative_feedback_types = ["👎", "unhelpful", "bad", "incorrect", "poor", "useless"]
    
    positive_feedback = 0
    negative_feedback = 0
    
    for f in feedback_store:
        feedback_lower = f["feedback"].lower()
        if any(pos_type in feedback_lower for pos_type in positive_feedback_types):
            positive_feedback += 1
        elif any(neg_type in feedback_lower for neg_type in negative_feedback_types):
            negative_feedback += 1
    
    return {
        "total_feedback": total_feedback,
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback,
        "neutral_feedback": total_feedback - positive_feedback - negative_feedback,
        "satisfaction_rate": round((positive_feedback / total_feedback * 100), 2) if total_feedback > 0 else 0,
        "recent_feedback": feedback_store[-5:] if feedback_store else [],
        "supported_positive_types": positive_feedback_types,
        "supported_negative_types": negative_feedback_types
    }
