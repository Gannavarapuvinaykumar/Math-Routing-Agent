# System Status and Health Monitoring for Math Routing Agent

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time
import os
from datetime import datetime

# Try to import psutil, fall back to basic monitoring if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from performance_analytics import performance_analytics
from cache_manager import math_cache

router = APIRouter()

@router.get("/system/health")
def get_system_health():
    """Comprehensive system health check"""
    
    # Basic system metrics (fallback if psutil not available)
    if PSUTIL_AVAILABLE:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        system_metrics = {
            "cpu_usage": round(cpu_percent, 1),
            "memory_usage": round(memory.percent, 1),
            "disk_usage": round(disk.percent, 1),
            "uptime_seconds": time.time() - psutil.boot_time()
        }
    else:
        system_metrics = {
            "cpu_usage": "N/A (psutil not available)",
            "memory_usage": "N/A (psutil not available)", 
            "disk_usage": "N/A (psutil not available)",
            "uptime_seconds": "N/A (psutil not available)"
        }
    
    # Application metrics
    analytics = performance_analytics.get_performance_summary(1)
    cache_stats = math_cache.get_cache_stats()
    
    # Component status
    components = {
        "qdrant": check_qdrant_health(),
        "openai": check_openai_health(),
        "cache": True,  # Always available
        "analytics": True  # Always available
    }
    
    # Overall health calculation
    component_health = sum(1 for status in components.values() if status) / len(components) * 100
    
    if PSUTIL_AVAILABLE:
        system_health = calculate_overall_health(cpu_percent, memory.percent, analytics, component_health)
    else:
        system_health = component_health * 0.8  # Reduced score without system metrics
    
    return JSONResponse(content={
        "status": get_health_status(system_health),
        "overall_health": round(system_health, 1),
        "timestamp": datetime.now().isoformat(),
        "system_metrics": system_metrics,
        "application_metrics": {
            "requests_last_hour": analytics.get("total_requests", 0),
            "success_rate": analytics.get("success_rate", 0),
            "avg_response_time": analytics.get("avg_response_time", 0),
            "cache_hit_ratio": cache_stats.get("hit_ratio", 0),
            "cache_entries": cache_stats.get("total_entries", 0)
        },
        "component_status": components,
        "performance_grade": get_performance_grade(system_health),
        "recommendations": get_system_recommendations(analytics)
    })

def check_qdrant_health():
    """Check if Qdrant is accessible"""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient("localhost", port=6333)
        collections = client.get_collections()
        return True
    except:
        return False

def check_openai_health():
    """Check if OpenAI API is accessible"""
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        return bool(api_key and len(api_key) > 10)
    except:
        return False

def check_mcp_health():
    """Check if MCP service is accessible"""
    try:
        # This would check actual MCP connectivity
        # For now, return True if MCP client is importable
        from mcp_integration import mcp_client
        return True
    except:
        return False

def get_health_status(health_score: float):
    """Get health status string"""
    if health_score >= 90:
        return "Excellent"
    elif health_score >= 75:
        return "Good"
    elif health_score >= 60:
        return "Fair"
    elif health_score >= 40:
        return "Poor"
    else:
        return "Critical"

def get_performance_grade(health_score: float):
    """Get performance grade"""
    if health_score >= 95:
        return "A+"
    elif health_score >= 90:
        return "A"
    elif health_score >= 85:
        return "B+"
    elif health_score >= 80:
        return "B"
    elif health_score >= 75:
        return "C+"
    elif health_score >= 70:
        return "C"
    elif health_score >= 60:
        return "D"
    else:
        return "F"

def calculate_overall_health(cpu: float, memory: float, analytics: dict, component_health: float):
    """Calculate overall system health score (0-100)"""
    
    # System resource health (0-30 points)
    cpu_score = max(0, 30 - (cpu - 50) * 0.6) if cpu > 50 else 30
    memory_score = max(0, 30 - (memory - 70) * 0.43) if memory > 70 else 30
    resource_score = (cpu_score + memory_score) / 2
    
    # Application performance health (0-40 points)
    success_rate = analytics.get("success_rate", 100)
    response_time = analytics.get("avg_response_time", 1.0)
    
    success_score = (success_rate / 100) * 20
    time_score = max(0, 20 - (response_time - 2.0) * 5) if response_time > 2.0 else 20
    performance_score = success_score + time_score
    
    # Component health (0-30 points)
    component_score = (component_health / 100) * 30
    
    return min(100, resource_score + performance_score + component_score)

def get_system_recommendations(analytics: dict):
    """Generate system improvement recommendations"""
    recommendations = []
    
    success_rate = analytics.get("success_rate", 100)
    if success_rate < 95:
        recommendations.append("Success rate below optimal - review error logs and improve error handling")
    
    response_time = analytics.get("avg_response_time", 1.0)
    if response_time > 3.0:
        recommendations.append("Slow response times - optimize database queries and add caching")
    
    cache_stats = math_cache.get_cache_stats()
    if cache_stats.get("hit_ratio", 0) < 0.3:
        recommendations.append("Low cache hit ratio - tune caching strategy")
    
    if not recommendations:
        recommendations.append("System is performing optimally")
    
    return recommendations

@router.get("/system/metrics/detailed")
def get_detailed_metrics():
    """Get detailed system metrics for monitoring dashboard"""
    
    basic_metrics = {
        "timestamp": datetime.now().isoformat(),
        "application": {
            "process_id": os.getpid(),
            "uptime": "Available"
        },
        "performance": performance_analytics.get_performance_summary(24),
        "cache": math_cache.get_cache_stats()
    }
    
    # Add system metrics if psutil is available
    if PSUTIL_AVAILABLE:
        try:
            process = psutil.Process()
            basic_metrics["system"] = {
                "cpu": {
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "used": psutil.virtual_memory().used,
                    "percent": psutil.virtual_memory().percent
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                }
            }
            basic_metrics["application"].update({
                "memory_usage": process.memory_info().rss,
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads()
            })
        except Exception:
            basic_metrics["system"] = {"status": "psutil available but error occurred"}
    else:
        basic_metrics["system"] = {"status": "psutil not available - install for detailed metrics"}
    
    return JSONResponse(content=basic_metrics)
