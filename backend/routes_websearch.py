import os
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:8080')

router = APIRouter()


class WebSearchRequest(BaseModel):
    query: str


@router.post("/web_search")
async def web_search(query: str | None = None, body: WebSearchRequest | None = Body(None)):
    """Route web search via local MCP client (falls back to Tavily if configured).

    Accepts either a query string as a URL/query parameter or a JSON body {"query": "..."}.
    """
    # Import guardrails and MCP client
    from guardrails import guardrails
    from mcp_integration import mcp_client

    # Determine the query text (prefer query param, else body)
    query_text = None
    if query:
        query_text = query
    elif body and getattr(body, "query", None):
        query_text = body.query

    if not query_text:
        raise HTTPException(status_code=422, detail=[{"type": "missing", "loc": ["query"], "msg": "Field required"}])

    # Validate input with guardrails
    valid, message = guardrails.process_request(query_text)
    if not valid:
        return {"result": message}

    try:
        # Use the local MCP client which will call Tavily if configured
        result = mcp_client.search(query_text, include_answer=True, search_depth="basic")

        # If the MCP client returned an error-like dict, map to clearer HTTP responses
        if isinstance(result, dict) and result.get("error"):
            err = result.get("error")
            # Known missing-key case
            if isinstance(err, str) and "Tavily API key not configured" in err:
                raise HTTPException(status_code=502, detail={
                    "error": "upstream_unavailable",
                    "message": "Tavily API key not configured on the server. Please set TAVILY_API_KEY in .env and restart.",
                    "upstream_message": err
                })

            # Upstream authentication failure (map to 502 with hint)
            if isinstance(err, str) and ("401" in err or "Unauthorized" in err or "authentication" in err.lower()):
                raise HTTPException(status_code=502, detail={
                    "error": "upstream_auth_failed",
                    "message": "Upstream search provider rejected the request (401). Check your TAVILY_API_KEY.",
                    "upstream_message": err
                })

            # Generic upstream error
            raise HTTPException(status_code=502, detail={
                "error": "upstream_search_error",
                "message": "Upstream search failed. See upstream_message for details.",
                "upstream_message": err
            })

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
        # Return a friendly structured error instead of raw exception
        raise HTTPException(status_code=500, detail={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "debug": str(e)
        })
