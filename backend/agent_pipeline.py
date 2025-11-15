
# Math Routing Agent: LangGraph Pipeline with Guardrails and Human Feedback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams
import os
import httpx
from dotenv import load_dotenv
import time
from datetime import datetime

# Import new modules
from guardrails import guardrails
from human_feedback import feedback_system
from mcp_integration import mcp_client
from cache_manager import math_cache
from performance_analytics import performance_analytics
from translation_service import translation_service

load_dotenv()
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Config with Windows Docker networking support
QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
COLLECTION_NAME = 'math_kb'
EMBED_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Try multiple connection approaches for Windows Docker
def get_qdrant_client():
    """Get Qdrant client with Windows Docker networking support"""
    hosts_to_try = ['127.0.0.1', 'localhost', 'host.docker.internal']
    
    for host in hosts_to_try:
        try:
            client = QdrantClient(
                host=host,
                port=QDRANT_PORT,
                timeout=10  # Shorter timeout for faster failover
            )
            # Test connection
            client.get_collections()
            return client
        except Exception:
            continue
    
    # If all fail, use the working host
    return QdrantClient(
        host='127.0.0.1', 
        port=QDRANT_PORT,
        timeout=15
    )

client = get_qdrant_client()
model = SentenceTransformer(EMBED_MODEL)

router = APIRouter()

def kb_search_tool(query: str):
    """Enhanced KB search with better handling for user-validated content"""
    try:
        # Normalization helper for exact-match detection
        def normalize_question(q: str) -> str:
            return " ".join(q.strip().lower().split())

        normalized_q = normalize_question(query)

        # If the query contains numeric literals, prefer exact normalized matches only
        import re
        contains_number = bool(re.search(r"\d", query))

        # First do a semantic search (top 10) and look for an exact normalized question match
        query_vec = model.encode(query).tolist()
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec,
            limit=10
        )

        if search_result:
            for res in search_result:
                payload = res.payload or {}
                if payload.get("question_norm") == normalized_q:
                    # Exact stored question match — return immediately with high confidence
                    return {
                        "question": payload.get("question"),
                        "answer": payload.get("answer"),
                        "steps": payload.get("steps"),
                        "topic": payload.get("topic"),
                        "subtopic": payload.get("subtopic"),
                        "difficulty": payload.get("difficulty"),
                        "source": "Knowledge Base (Exact)",
                        "original_source": payload.get("source"),
                        "validated_by_user": payload.get("validated_by_user", False),
                        "score": res.score
                    }

        # If the incoming query contains numbers and we did not find an exact normalized match,
        # do not fall back to returning other semantically similar entries (to avoid numeric mismatches).
        if contains_number:
            return None

        # No exact normalized match; fall back to semantic logic (top 3)
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec,
            limit=3
        )

        if not search_result:
            return None

        # Check results - prioritize user-validated content with lower threshold
        for result in search_result:
            payload = result.payload or {}
            score = result.score

            # User-validated content gets lower threshold (more lenient)
            if payload.get("validated_by_user") or payload.get("route_origin") in ["web", "ai"]:
                if score >= 0.45:  # Lower threshold for validated content
                    print(f"✅ Found user-validated content! Score: {score}")
                    return {
                        "question": payload.get("question"),
                        "answer": payload.get("answer"),
                        "steps": payload.get("steps"),
                        "topic": payload.get("topic"),
                        "subtopic": payload.get("subtopic"),
                        "difficulty": payload.get("difficulty"),
                        "source": "Knowledge Base (User Validated)",
                        "original_source": payload.get("source"),
                        "validated_by_user": True,
                        "score": score
                    }

            # Regular KB content uses normal threshold
            elif score >= 0.65:
                return {
                    "question": payload.get("question"),
                    "answer": payload.get("answer"),
                    "steps": payload.get("steps"),
                    "topic": payload.get("topic"),
                    "subtopic": payload.get("subtopic"),
                    "difficulty": payload.get("difficulty"),
                    "source": "Knowledge Base",
                    "original_source": payload.get("source"),
                    "score": score
                }

        # No good matches found
        return None

    except Exception as e:
        print(f"❌ KB search error: {e}")
        return {
            "error": f"KB search failed: {str(e)}",
            "source": "Knowledge Base Error"
        }

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str

class FeedbackRequest(BaseModel):
    query: str
    ai_solution: str
    human_feedback: str
    rating: int

# Use MCP client for web search
def web_search_tool(query: str):
    """Web search using MCP integration"""
    try:
        result = mcp_client.search(query, include_answer=True, search_depth="basic")
        
        if "error" in result:
            return {
                "error": result["error"],
                "source": "MCP Web Search"
            }
        
        return {
            "answer": result.get("answer", "No answer found"),
            "summary": result.get("summary", "No summary available"),
            "sources": result.get("sources", []),
            "source": "MCP Web Search",
            "metadata": result.get("search_metadata", {})
        }
        
    except Exception as e:
        return {
            "error": f"MCP search failed: {str(e)}",
            "source": "MCP Web Search"
        }# OpenAI AI model for generating solutions
def openai_solve_tool(query: str):
    from openai import OpenAI
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""You are a math professor. Solve this step-by-step: {query}

Format your response as:
Answer: [final answer]
Steps:
1. [step 1]
2. [step 2]
3. [step 3]
...

Be clear and educational."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert math professor who explains solutions clearly and step-by-step."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "answer": "Generated by AI",
            "steps": ai_response,
            "source": "OpenAI GPT",
            "model": "gpt-4"
        }
    except Exception as e:
        return {"message": f"AI generation failed: {str(e)}. Human feedback required."}

# Guardrail: Only allow math/education queries
def input_guardrail(query: str):
	allowed_keywords = [
		"solve", "integrate", "differentiate", "limit", "probability", "equation", "geometry", "algebra", "calculus",
		"derivative", "find", "compute", "step", "math", "expression", "function", "value", "simplify", "expand",
		"proof", "theorem", "explain", "detail"
	]
	# Allow if any keyword is present, or if the query contains 'derivative' or 'differentiate'
	query_lower = query.lower()
	if any(kw in query_lower for kw in allowed_keywords):
		return True
	# Allow if query looks like a math expression (contains ^, +, -, *, /, =)
	math_chars = set('^+-*/=')
	if any(c in query for c in math_chars):
		return True
	return False


def persist_to_kb(route_origin: str, query: str, answer: str, steps: str | None = None, sources: list | None = None, metadata: dict | None = None):
    """Persist a Q&A pair into the Qdrant `math_kb` collection.

    route_origin: one of 'web', 'ai', 'human', or 'kb'
    """
    try:
        # Use the question alone for the KB vector so future searches (query embeddings)
        # match the stored points reliably. Storing the question-only vector improves
        # recall when users re-ask the same or similar questions.
        vec = model.encode(query).tolist()

        # Normalized question for exact-match detection
        def normalize_question(q: str) -> str:
            return " ".join(q.strip().lower().split())

        question_norm = normalize_question(query)

        payload = {
            "question": query,
            "question_norm": question_norm,
            "answer": answer,
            "steps": steps,
            "topic": metadata.get("topic") if metadata else None,
            "subtopic": metadata.get("subtopic") if metadata else None,
            "difficulty": metadata.get("difficulty") if metadata else None,
            "source": route_origin,
            "route_origin": route_origin,
            "validated_by_user": False,
            "created_at": datetime.utcnow().isoformat(),
            "additional_sources": sources or []
        }

        # Build a candidate point; id may be replaced if we find an existing similar point
        new_point = {
            "id": int(time.time() * 1000),
            "vector": vec,
            "payload": payload
        }

        # Deduplication: search for exact normalized question match first, then for extremely similar vectors
        try:
            search_candidates = client.search(collection_name=COLLECTION_NAME, query_vector=vec, limit=5)
            existing_id = None
            for cand in search_candidates:
                cand_payload = cand.payload or {}
                # Exact normalized question match -> update that point
                if cand_payload.get("question_norm") == question_norm:
                    existing_id = getattr(cand, "id", None) or cand.payload.get("id")
                    print(f"Found existing exact KB entry (id={existing_id}), updating instead of inserting.")
                    break
            # If no exact match, check for almost-identical vector (very high similarity)
            if existing_id is None:
                for cand in search_candidates:
                    score = getattr(cand, "score", None)
                    if score is not None and score >= 0.95:
                        existing_id = getattr(cand, "id", None) or cand.payload.get("id")
                        print(f"Found very similar KB entry (id={existing_id}, score={score}), updating instead of inserting.")
                        break

            if existing_id:
                # Overwrite id so upsert performs update
                new_point["id"] = existing_id
        except Exception:
            # If search fails (e.g., collection missing), we'll rely on the normal upsert/create flow below
            pass

        try:
            client.upsert(collection_name=COLLECTION_NAME, points=[new_point])
            print(f"Stored new KB item from {route_origin} for query: {query}")
            return True
        except Exception as e:
            # If the collection does not exist, create it with the correct vector size and retry once
            err = str(e)
            print(f"Error persisting to KB: {e}")
            if "doesn't exist" in err or "Not found" in err or 'Collection' in err and 'doesn' in err:
                try:
                    vec_size = len(vec)
                    print(f"Creating missing collection '{COLLECTION_NAME}' with vector size {vec_size} (no destructive operations)")
                    # Create the collection only if it does not exist to avoid data loss
                    existing = [c.name for c in client.get_collections().collections]
                    if COLLECTION_NAME not in existing:
                        client.create_collection(
                            collection_name=COLLECTION_NAME,
                            vectors_config=VectorParams(size=vec_size, distance="Cosine")
                        )
                    else:
                        print(f"Collection '{COLLECTION_NAME}' unexpectedly exists after NotFound error; skipping creation to avoid data loss")
                    # Retry upsert
                    client.upsert(collection_name=COLLECTION_NAME, points=[new_point])
                    print(f"Stored new KB item after creating collection: {query}")
                    return True
                except Exception as e2:
                    print(f"Failed to create collection or persist point: {e2}")
            else:
                # Other errors; just log
                print(f"Unhandled error persisting to KB: {e}")
            return False
    except Exception as e:
        print(f"Error persisting to KB: {e}")
        return False
    return False

# Enhanced routing pipeline with guardrails and analytics
@router.post("/agent_route")
def agent_route(request: QueryRequest):
    """Enhanced agent routing with full guardrails, analytics, and caching support"""
    query = request.query
    
    # Start performance tracking
    tracking_id = performance_analytics.log_request_start(query)
    
    # Check cache first
    cached_result = math_cache.get(query)
    if cached_result:
        # Get the original route from cache
        original_route = math_cache.get_route_info(query) or "Cache"
        
        performance_analytics.log_request_end(tracking_id, original_route, True, 1.0)
        return JSONResponse(content={
            "route": original_route,  # Use original route instead of "Cache"
            "result": cached_result, 
            "confidence": "high",
            "cached": True,
            "trace_id": tracking_id
        })
    
    # Input guardrails
    is_valid, validation_message = guardrails.process_request(query)
    if not is_valid:
        # Log violation and block query
        performance_analytics.log_request_end(tracking_id, "Blocked", False, error=validation_message)
        # Optionally log to console for debugging
        print(f"Guardrail blocked query: {query} | Reason: {validation_message}")
        return JSONResponse(
            status_code=400,
            content={
                "error": validation_message,
                "route": "blocked",
                "message": "Your query was blocked by guardrails. Please ask a math or education-related question."
            }
        )
    
    # Try KB search first with enhanced logic for user-validated content
    kb_result = kb_search_tool(query)
    if kb_result:
        # Different thresholds for different content types
        score = kb_result.get('score', 0)
        is_validated = kb_result.get('validated_by_user', False)
        
        # Lower threshold for user-validated content (0.45) vs regular KB (0.65)
        threshold = 0.45 if is_validated else 0.65
        
        if score >= threshold:
            # Validate output
            is_valid, message, filtered_result = guardrails.process_response(kb_result)
            if is_valid:
                # Cache the KB result
                math_cache.set(query, filtered_result, "KB")
                performance_analytics.log_request_end(tracking_id, "KB", True, 1.0)
                
                # Add validation info to response
                response_data = {
                    "route": "KB", 
                    "result": filtered_result, 
                    "confidence": "high" if score >= 0.65 else "medium",
                    "trace_id": tracking_id
                }
                
                if is_validated:
                    response_data["validation_info"] = "This response was previously validated by user feedback"
                
                return JSONResponse(content=response_data)
    
    # Check for AI-first keywords (invention, creation, fictional scenarios)
    ai_first_keywords = ["invent", "create", "design", "flurble", "fictional", "imagine", "suppose", "pretend", "novel", "new mathematical operation"]
    query_lower = query.lower()
    skip_web_search = any(keyword in query_lower for keyword in ai_first_keywords)
    
    # Try web search via MCP (skip if AI-first keywords detected)
    if not skip_web_search:
        web_result = web_search_tool(query)
        if web_result and "answer" in web_result and "error" not in web_result:
            # Validate output
            is_valid, message, filtered_result = guardrails.process_response(web_result)
            if is_valid:
                # Persist web answer to KB (store question+answer for future retrieval)
                try:
                    persisted = persist_to_kb(
                        route_origin="web",
                        query=query,
                        answer=filtered_result.get("answer") if isinstance(filtered_result, dict) else web_result.get("answer"),
                        steps=filtered_result.get("steps") if isinstance(filtered_result, dict) else web_result.get("steps"),
                        sources=filtered_result.get("sources") if isinstance(filtered_result, dict) else web_result.get("sources"),
                        metadata=filtered_result.get("metadata") if isinstance(filtered_result, dict) else web_result.get("metadata")
                    )
                except Exception:
                    persisted = False

                # If we successfully persisted to KB, cache as KB so next requests hit KB immediately.
                cache_route = "KB" if persisted else "Web"
                math_cache.set(query, filtered_result, cache_route)
                performance_analytics.log_request_end(tracking_id, "Web", True, 1.0)
                
                return JSONResponse(content={
                    "route": "Web", 
                    "result": filtered_result, 
                    "confidence": "medium",
                    "trace_id": tracking_id
                })
    
    # Try AI generation
    ai_result = openai_solve_tool(query)
    if ai_result and "answer" in ai_result and "error" not in ai_result:
        # Validate output
        is_valid, message, filtered_result = guardrails.process_response(ai_result)
        if is_valid:
            # Persist AI answer to KB
            try:
                persisted_ai = persist_to_kb(
                    route_origin="ai",
                    query=query,
                    answer=filtered_result.get("answer") if isinstance(filtered_result, dict) else ai_result.get("answer"),
                    steps=filtered_result.get("steps") if isinstance(filtered_result, dict) else ai_result.get("steps"),
                    sources=filtered_result.get("sources") if isinstance(filtered_result, dict) else ai_result.get("sources"),
                    metadata=filtered_result.get("metadata") if isinstance(filtered_result, dict) else ai_result.get("metadata")
                )
            except Exception:
                persisted_ai = False

            # If persisted, cache as KB so subsequent identical queries hit KB
            cache_route = "KB" if persisted_ai else "AI"
            math_cache.set(query, filtered_result, cache_route)
            performance_analytics.log_request_end(tracking_id, "AI", True, 1.0)
            
            return JSONResponse(content={
                "route": "AI", 
                "result": filtered_result, 
                "confidence": "medium",
                "trace_id": tracking_id
            })
    
    # Require human feedback
    human_result = feedback_system.require_human_feedback(query)
    return JSONResponse(content={
        "route": "Human", 
        "result": human_result, 
        "confidence": "low",
        "trace_id": tracking_id
    })

# Human feedback submission endpoint
@router.post("/submit_feedback")
def submit_feedback(request: FeedbackRequest):
    """Submit human feedback for learning"""
    result = feedback_system.submit_feedback(
        query=request.query,
        ai_solution=request.ai_solution,
        human_feedback=request.human_feedback,
        rating=request.rating
    )
    return JSONResponse(content=result)

# Feedback statistics endpoint
@router.get("/feedback_stats")
def get_feedback_stats():
    """Get feedback system statistics"""
    stats = feedback_system.get_feedback_stats()
    return JSONResponse(content=stats)

# Guardrails statistics endpoint
@router.get("/guardrails_stats")
def get_guardrails_stats():
    """Get guardrails violation statistics"""
    stats = guardrails.get_violation_stats()
    return JSONResponse(content=stats)

# MCP capabilities endpoint
@router.get("/mcp_capabilities")
def get_mcp_capabilities():
    """Get MCP server capabilities"""
    capabilities = mcp_client.get_capabilities()
    return JSONResponse(content=capabilities)

# MCP search history endpoint
@router.get("/mcp_history")
def get_mcp_history(limit: int = 10):
    """Get MCP search history"""
    history = mcp_client.get_search_history(limit)
    return JSONResponse(content={"history": history})

# Performance Analytics Endpoints
@router.get("/analytics/performance")
def get_performance_analytics(hours: int = 24):
    """Get comprehensive performance analytics"""
    analytics = performance_analytics.get_performance_summary(hours)
    return JSONResponse(content=analytics)

@router.get("/analytics/cache")
def get_cache_analytics():
    """Get cache performance statistics"""
    cache_stats = math_cache.get_cache_stats()
    return JSONResponse(content=cache_stats)

@router.post("/analytics/feedback")
def submit_analytics_feedback(tracking_id: str, rating: int, feedback: str = ""):
    """Submit feedback for analytics tracking"""
    performance_analytics.log_user_feedback(tracking_id, rating, feedback)
    return JSONResponse(content={"success": True, "message": "Feedback recorded for analytics"})

@router.get("/analytics/system-health")
def get_system_health():
    """Get real-time system health metrics"""
    analytics = performance_analytics.get_performance_summary(1)  # Last hour
    return JSONResponse(content={
        "status": "healthy",
        "metrics": analytics,
        "timestamp": "2025-09-04T00:00:00Z"
    })

