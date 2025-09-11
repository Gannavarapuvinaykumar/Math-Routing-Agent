"""
LangGraph Agent Framework for Math Routing Agent
"""
from langgraph.graph import Graph, END
from langgraph.prebuilt import ToolExecutor
from langchain.tools import BaseTool
from typing import Dict, List, Any, Optional, TypedDict
import json
from datetime import datetime

class AgentState(TypedDict):
    """State object for the agent graph"""
    query: str
    route: str
    result: Optional[Dict]
    confidence: str
    error: Optional[str]
    attempts: List[str]
    metadata: Dict

class KnowledgeBaseTool(BaseTool):
    """Knowledge Base search tool"""
    name = "knowledge_base_search"
    description = "Search the mathematical knowledge base for exact matches"
    
    def _run(self, query: str) -> Dict:
        from agent_pipeline import kb_search_tool
        result = kb_search_tool(query)
        return result or {"error": "No KB match found"}

class WebSearchTool(BaseTool):
    """Web search tool using MCP"""
    name = "web_search"
    description = "Search the web for mathematical information using MCP"
    
    def _run(self, query: str) -> Dict:
        from mcp_integration import mcp_client
        result = mcp_client.search(query)
        return result

class AIGenerationTool(BaseTool):
    """AI generation tool"""
    name = "ai_generation"
    description = "Generate mathematical solutions using OpenAI"
    
    def _run(self, query: str) -> Dict:
        from agent_pipeline import openai_solve_tool
        result = openai_solve_tool(query)
        return result

class HumanFeedbackTool(BaseTool):
    """Human feedback tool"""
    name = "human_feedback"
    description = "Request human feedback for complex queries"
    
    def _run(self, query: str) -> Dict:
        from human_feedback import feedback_system
        result = feedback_system.require_human_feedback(query)
        return result

class MathRoutingAgent:
    """LangGraph-based Math Routing Agent"""
    
    def __init__(self):
        self.tools = [
            KnowledgeBaseTool(),
            WebSearchTool(),
            AIGenerationTool(),
            HumanFeedbackTool()
        ]
        self.tool_executor = ToolExecutor(self.tools)
        self.graph = self._create_graph()
    
    def _create_graph(self) -> Graph:
        """Create the agent routing graph"""
        graph = Graph()
        
        # Add nodes
        graph.add_node("input_validation", self.validate_input)
        graph.add_node("kb_search", self.search_knowledge_base)
        graph.add_node("web_search", self.search_web)
        graph.add_node("ai_generation", self.generate_ai_solution)
        graph.add_node("human_feedback", self.request_human_feedback)
        graph.add_node("output_validation", self.validate_output)
        
        # Add edges (routing logic)
        graph.add_edge("input_validation", "kb_search")
        graph.add_conditional_edges(
            "kb_search",
            self.should_continue_from_kb,
            {
                "web_search": "web_search",
                "output_validation": "output_validation"
            }
        )
        graph.add_conditional_edges(
            "web_search",
            self.should_continue_from_web,
            {
                "ai_generation": "ai_generation",
                "output_validation": "output_validation"
            }
        )
        graph.add_conditional_edges(
            "ai_generation",
            self.should_continue_from_ai,
            {
                "human_feedback": "human_feedback",
                "output_validation": "output_validation"
            }
        )
        graph.add_edge("human_feedback", "output_validation")
        graph.add_edge("output_validation", END)
        
        # Set entry point
        graph.set_entry_point("input_validation")
        
        return graph.compile()
    
    def validate_input(self, state: AgentState) -> AgentState:
        """Validate input using guardrails"""
        from guardrails import guardrails
        
        query = state["query"]
        is_valid, message = guardrails.process_request(query)
        
        if not is_valid:
            state["error"] = message
            state["route"] = "error"
            return state
        
        state["attempts"] = []
        state["metadata"] = {"start_time": datetime.now().isoformat()}
        return state
    
    def search_knowledge_base(self, state: AgentState) -> AgentState:
        """Search knowledge base"""
        kb_tool = next(tool for tool in self.tools if tool.name == "knowledge_base_search")
        result = kb_tool._run(state["query"])
        
        state["attempts"].append("kb_search")
        
        if result and "error" not in result and result.get("score", 0) >= 0.8:
            state["route"] = "KB"
            state["result"] = result
            state["confidence"] = "high"
        else:
            state["result"] = None
        
        return state
    
    def search_web(self, state: AgentState) -> AgentState:
        """Search web using MCP"""
        web_tool = next(tool for tool in self.tools if tool.name == "web_search")
        result = web_tool._run(state["query"])
        
        state["attempts"].append("web_search")
        
        if result and "error" not in result and result.get("answer"):
            state["route"] = "Web"
            state["result"] = result
            state["confidence"] = "medium"
        else:
            state["result"] = None
        
        return state
    
    def generate_ai_solution(self, state: AgentState) -> AgentState:
        """Generate AI solution"""
        ai_tool = next(tool for tool in self.tools if tool.name == "ai_generation")
        result = ai_tool._run(state["query"])
        
        state["attempts"].append("ai_generation")
        
        if result and "error" not in result and result.get("answer"):
            state["route"] = "AI"
            state["result"] = result
            state["confidence"] = "medium"
        else:
            state["result"] = None
        
        return state
    
    def request_human_feedback(self, state: AgentState) -> AgentState:
        """Request human feedback"""
        human_tool = next(tool for tool in self.tools if tool.name == "human_feedback")
        result = human_tool._run(state["query"])
        
        state["attempts"].append("human_feedback")
        state["route"] = "Human"
        state["result"] = result
        state["confidence"] = "low"
        
        return state
    
    def validate_output(self, state: AgentState) -> AgentState:
        """Validate output using guardrails"""
        from guardrails import guardrails
        
        if state.get("result"):
            is_valid, message, filtered_result = guardrails.process_response(state["result"])
            
            if is_valid:
                state["result"] = filtered_result
            else:
                state["error"] = message
                state["route"] = "error"
        
        state["metadata"]["end_time"] = datetime.now().isoformat()
        state["metadata"]["total_attempts"] = len(state["attempts"])
        
        return state
    
    def should_continue_from_kb(self, state: AgentState) -> str:
        """Decide next step after KB search"""
        if state.get("result") and state.get("confidence") == "high":
            return "output_validation"
        return "web_search"
    
    def should_continue_from_web(self, state: AgentState) -> str:
        """Decide next step after web search"""
        if state.get("result") and state.get("confidence") == "medium":
            return "output_validation"
        return "ai_generation"
    
    def should_continue_from_ai(self, state: AgentState) -> str:
        """Decide next step after AI generation"""
        if state.get("result") and state.get("confidence") == "medium":
            return "output_validation"
        return "human_feedback"
    
    def process_query(self, query: str) -> Dict:
        """Process a query through the agent graph"""
        initial_state = AgentState(
            query=query,
            route="",
            result=None,
            confidence="",
            error=None,
            attempts=[],
            metadata={}
        )
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            return {
                "route": final_state.get("route", "error"),
                "result": final_state.get("result", {}),
                "confidence": final_state.get("confidence", "none"),
                "error": final_state.get("error"),
                "metadata": final_state.get("metadata", {}),
                "attempts": final_state.get("attempts", [])
            }
            
        except Exception as e:
            return {
                "route": "error",
                "result": {},
                "confidence": "none",
                "error": f"Agent processing failed: {str(e)}",
                "metadata": {},
                "attempts": []
            }

# Global agent instance
math_agent = MathRoutingAgent()
