import os
import httpx
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:8080')

router = APIRouter()

@router.post("/web_search")
async def web_search(query: str):
    """Route web search via MCP Tavily server."""
    # Import guardrails
    from guardrails import guardrails
    # Validate input with guardrails
    valid, message = guardrails.validate_input(query)
    if not valid:
        return {"result": message}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{MCP_SERVER_URL}/web.search", json={"query": query})
            resp.raise_for_status()
            result = resp.json()
            
            # Validate output with guardrails
            if result and isinstance(result, dict):
                is_valid, message, filtered_result = guardrails.process_response(result)
                if is_valid:
                    return filtered_result
                else:
                    raise HTTPException(status_code=400, detail={
                        "error": message,
                        "route": "blocked",
                        "message": "Response was blocked by output guardrails."
                    })
            
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
