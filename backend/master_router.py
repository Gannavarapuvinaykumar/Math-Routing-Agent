from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import tools from agent_pipeline
from agent_pipeline import kb_search_tool, web_search_tool, openai_solve_tool, persist_to_kb
from human_feedback import feedback_system

router = APIRouter()

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_math(request: AskRequest):
    query = request.question

    # 1) Try KB first
    try:
        kb_result = kb_search_tool(query)
    except Exception as e:
        kb_result = None

    if kb_result:
        # kb_result may already be formatted; return directly
        return {"answer": kb_result, "source": "KB"}

    # 2) Web search
    try:
        web_result = web_search_tool(query)
    except Exception as e:
        web_result = None

    if web_result and not (isinstance(web_result, dict) and web_result.get("error")):
        # web_result might be dict with 'answer' or a plain string
        if isinstance(web_result, dict):
            answer = web_result.get("answer") or web_result.get("summary") or str(web_result)
            sources = web_result.get("sources") if isinstance(web_result.get("sources"), list) else []
            metadata = web_result.get("metadata") if isinstance(web_result.get("metadata"), dict) else {}
        else:
            answer = str(web_result)
            sources = []
            metadata = {}

        # Persist into KB
        try:
            persist_to_kb(route_origin="web", query=query, answer=answer, steps=None, sources=sources, metadata=metadata)
        except Exception:
            pass

        return {"answer": answer, "source": "WEB"}

    # 3) AI generation
    try:
        ai_result = openai_solve_tool(query)
    except Exception as e:
        ai_result = None

    if ai_result and not (isinstance(ai_result, dict) and ai_result.get("error")):
        if isinstance(ai_result, dict):
            answer = ai_result.get("answer") or ai_result.get("steps") or str(ai_result)
            steps = ai_result.get("steps") if isinstance(ai_result.get("steps"), (str, list)) else None
            metadata = ai_result.get("metadata") if isinstance(ai_result.get("metadata"), dict) else {}
        else:
            answer = str(ai_result)
            steps = None
            metadata = {}

        # Persist into KB
        try:
            persist_to_kb(route_origin="ai", query=query, answer=answer, steps=steps, sources=None, metadata=metadata)
        except Exception:
            pass

        return {"answer": answer, "source": "AI"}

    # 4) Human expert
    human_answer = feedback_system.require_human_feedback(query)
    # feedback_system.require_human_feedback returns a dict instructing action; in production this should trigger a human workflow
    if human_answer:
        # If human provides an actual answer through feedback submission, it will be stored by the feedback system
        return {"answer": human_answer, "source": "HUMAN"}

    # If all else fails
    raise HTTPException(status_code=500, detail="Unable to provide an answer at this time.")
