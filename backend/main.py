# Math Routing Agent Backend - Enhanced Version 2.0

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
from datetime import datetime
import os

# Import all route modules
from routes_websearch import router as websearch_router
from routes_kb import router as kb_router
from routes_feedback import router as feedback_router
from routes_pdf import router as pdf_router
from routes_openai import router as openai_router
from agent_pipeline import router as agent_router

# Import new enhanced modules
from system_monitor import router as monitor_router
from performance_analytics import performance_analytics
from cache_manager import math_cache
from translation_service import translation_service
from master_router import router as master_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI with enhanced metadata
app = FastAPI(
    title="Math Routing Agent",
    description="Advanced Mathematical Problem Solving with Multi-tier Routing, LaTeX Support, Caching, and Performance Analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for frontend with enhanced configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialize application services"""
    logger.info("Math Routing Agent starting up...")
    
    # Analytics and cache are auto-initialized on first use
    logger.info("Performance analytics ready")
    logger.info("Math cache ready")
    logger.info("Translation service ready")
    # Basic environment / API key checks to help diagnose web/AI failures
    tavily_key = os.getenv("TAVILY_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    def _mask(key: str):
        if not key:
            return None
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "..." + key[-4:]

    if not tavily_key:
        logger.warning("TAVILY_API_KEY is not set. Web search via Tavily will fail.")
    else:
        if tavily_key.startswith("ghp_") or tavily_key.startswith("gho_"):
            logger.warning("TAVILY_API_KEY looks like a GitHub token (starts with ghp_/gho_). Please verify the Tavily API key.")
        logger.info(f"TAVILY_API_KEY present: {_mask(tavily_key)}")

    if not openai_key:
        logger.warning("OPENAI_API_KEY is not set. AI generation via OpenAI will fail.")
    else:
        logger.info(f"OPENAI_API_KEY present: {_mask(openai_key)}")

    logger.info("Math Routing Agent startup complete")

@app.get("/")
def root():
    """Enhanced root endpoint with system information"""
    return JSONResponse(content={
        "message": "Math Routing Agent Backend v2.0 - Enhanced Edition",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Multi-tier routing (KB → Web → AI → Human)",
            "LaTeX mathematical notation support",
            "Advanced caching with LRU eviction",
            "Real-time performance analytics",
            "Multi-language support",
            "Integrated monitoring dashboard",
            "Quality scoring and feedback",
            "Vector database semantic search",
            "🆕 Auto KB storage for validated responses"
        ],
        "new_feature": {
            "kb_auto_storage": "Positive feedback automatically stores web/AI responses in KB for future use",
            "endpoint": "/api/feedback_with_storage",
            "supported_routes": ["Web", "AI"],
            "positive_feedback_types": ["👍", "helpful", "good", "excellent", "accurate", "useful"]
        },
        "endpoints": {
            "agent": "/api/agent_route",
            "search": "/api/search", 
            "feedback": "/api/feedback_with_storage",
            "analytics": "/api/stats",
            "health": "/api/status",
            "docs": "/docs"
        }
    })

@app.get("/api/status")
def get_status():
    """Quick status check endpoint"""
    cache_stats = math_cache.get_cache_stats()
    analytics = performance_analytics.get_performance_summary(1)
    
    return JSONResponse(content={
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "cache": {
            "entries": cache_stats.get("total_entries", 0),
            "hit_ratio": round(cache_stats.get("hit_ratio", 0), 2)
        },
        "performance": {
            "requests_last_hour": analytics.get("total_requests", 0),
            "success_rate": round(analytics.get("success_rate", 100), 1),
            "avg_response_time": round(analytics.get("avg_response_time", 0), 2)
        }
    })


@app.get("/api/diagnostics")
def diagnostics():
    """Expose masked diagnostics for environment and quick guidance"""
    tavily_key = os.getenv("TAVILY_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    def _mask(key: str):
        if not key:
            return None
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "..." + key[-4:]

    return JSONResponse(content={
        "tavily_key_present": bool(tavily_key),
        "tavily_key_masked": _mask(tavily_key),
        "openai_key_present": bool(openai_key),
        "openai_key_masked": _mask(openai_key),
        "advice": "If web search or AI generation fails, ensure these keys are correctly set in backend/.env and restart the server."
    })

# Enhanced feedback endpoint with KB storage
from pydantic import BaseModel

class EnhancedFeedbackRequest(BaseModel):
    trace_id: str
    query: str
    response: str
    route: str
    feedback: str  # "👍" or "👎"
    correction: str = None

@app.post("/api/feedback_with_storage")
async def submit_feedback_with_storage(request: EnhancedFeedbackRequest):
    """Submit feedback and automatically store validated responses in KB"""
    
    # Define positive feedback types that trigger KB storage
    positive_feedback_types = ["👍", "helpful", "good", "excellent", "accurate", "useful"]
    feedback_lower = request.feedback.lower()
    
    # Check if feedback is positive
    is_positive_feedback = any(pos_type in feedback_lower for pos_type in positive_feedback_types)
    
    # If positive feedback for web/AI generation, store in KB
    if is_positive_feedback and request.route.lower() in ["web", "ai", "web_search", "ai_generation"]:
        try:
            from routes_feedback import store_validated_response_in_kb
            
            success = store_validated_response_in_kb(
                query=request.query,
                response=request.response,
                source_route=request.route.lower()
            )
            
            if success:
                return {
                    "status": "success",
                    "message": f"✅ Feedback '{request.feedback}' submitted and response stored in KB for future use!",
                    "stored_in_kb": True,
                    "trace_id": request.trace_id,
                    "info": f"Your '{request.feedback}' feedback for this {request.route} response helped improve the knowledge base!"
                }
            else:
                return {
                    "status": "partial_success", 
                    "message": f"Feedback '{request.feedback}' submitted but failed to store in KB",
                    "stored_in_kb": False,
                    "trace_id": request.trace_id
                }
                
        except Exception as e:
            logger.error(f"Error storing validated response: {e}")
            return {
                "status": "partial_success",
                "message": f"Feedback '{request.feedback}' submitted but KB storage failed",
                "error": str(e),
                "stored_in_kb": False,
                "trace_id": request.trace_id
            }
    
    # Regular feedback (no KB storage for KB route or negative feedback)
    return {
        "status": "success",
        "message": f"Feedback '{request.feedback}' submitted successfully",
        "stored_in_kb": False,
        "trace_id": request.trace_id,
        "info": f"KB responses and non-positive feedback are not stored in KB. Positive feedback types: 👍, helpful, good, excellent, accurate, useful"
    }

# Register all route modules
app.include_router(websearch_router, prefix="/api", tags=["Web Search"])
app.include_router(kb_router, prefix="/api", tags=["Knowledge Base"])
app.include_router(feedback_router, prefix="/api", tags=["Feedback"])
app.include_router(pdf_router, prefix="/api", tags=["PDF"])
app.include_router(openai_router, prefix="/api", tags=["OpenAI"])
app.include_router(agent_router, prefix="/api", tags=["Agent Pipeline"])

# Register new enhanced modules
app.include_router(monitor_router, prefix="/api", tags=["System Monitoring"])
app.include_router(master_router, prefix="/api", tags=["Master Router"]) 

# Exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with logging"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
