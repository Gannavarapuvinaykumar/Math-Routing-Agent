"""
MCP (Model Context Protocol) Integration for Web Search
Since the Docker MCP server is not available, we'll implement MCP-style structured communication
"""
import httpx
import json
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

class MCPMessage:
    """MCP-style message structure"""
    def __init__(self, method: str, params: Dict = None, id: str = None):
        self.method = method
        self.params = params or {}
        self.id = id or str(datetime.now().timestamp())
        self.jsonrpc = "2.0"
    
    def to_dict(self):
        return {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id
        }

class MCPResponse:
    """MCP-style response structure"""
    def __init__(self, result: Any = None, error: Dict = None, id: str = None):
        self.result = result
        self.error = error
        self.id = id
        self.jsonrpc = "2.0"
    
    def to_dict(self):
        response = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response

class MCPWebSearchServer:
    """MCP-compliant web search server implementation"""
    
    def __init__(self):
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.search_history = []
        self.capabilities = {
            "search": {
                "description": "Perform web search for mathematical content",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "search_depth": {"type": "string", "enum": ["basic", "advanced"], "default": "basic"},
                    "include_answer": {"type": "boolean", "default": True},
                    "include_raw_content": {"type": "boolean", "default": False}
                }
            }
        }
    
    def handle_request(self, message: MCPMessage) -> MCPResponse:
        """Handle MCP request"""
        try:
            if message.method == "search":
                return self._handle_search(message)
            elif message.method == "capabilities":
                return self._handle_capabilities(message)
            elif message.method == "history":
                return self._handle_history(message)
            else:
                return MCPResponse(
                    error={"code": -32601, "message": f"Method '{message.method}' not found"},
                    id=message.id
                )
        except Exception as e:
            return MCPResponse(
                error={"code": -32603, "message": f"Internal error: {str(e)}"},
                id=message.id
            )
    
    def _handle_search(self, message: MCPMessage) -> MCPResponse:
        """Handle search request"""
        params = message.params
        query = params.get("query")
        
        if not query:
            return MCPResponse(
                error={"code": -32602, "message": "Missing required parameter 'query'"},
                id=message.id
            )
        
        # Perform Tavily search
        search_result = self._perform_tavily_search(
            query=query,
            search_depth=params.get("search_depth", "basic"),
            include_answer=params.get("include_answer", True),
            include_raw_content=params.get("include_raw_content", False)
        )
        
        # Log search
        self.search_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "result_summary": search_result.get("answer", "No answer")[:100]
        })
        
        # Keep only last 50 searches
        if len(self.search_history) > 50:
            self.search_history = self.search_history[-50:]
        
        return MCPResponse(result=search_result, id=message.id)
    
    def _handle_capabilities(self, message: MCPMessage) -> MCPResponse:
        """Handle capabilities request"""
        return MCPResponse(result=self.capabilities, id=message.id)
    
    def _handle_history(self, message: MCPMessage) -> MCPResponse:
        """Handle search history request"""
        limit = message.params.get("limit", 10)
        return MCPResponse(
            result={"history": self.search_history[-limit:]}, 
            id=message.id
        )
    
    def _perform_tavily_search(self, query: str, search_depth: str = "basic", 
                              include_answer: bool = True, include_raw_content: bool = False) -> Dict:
        """Perform actual Tavily API search"""
        if not self.tavily_api_key:
            return {
                "error": "Tavily API key not configured",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            tavily_url = 'https://api.tavily.com/search'
            headers = {'Authorization': f'Bearer {self.tavily_api_key}'}
            payload = {
                "query": query,
                "search_depth": search_depth,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content
            }
            
            response = httpx.post(tavily_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Structure response in MCP format
            mcp_result = {
                "query": query,
                "answer": data.get("answer", "No direct answer found"),
                "summary": data.get("summary", "No summary available"),
                "sources": data.get("results", [])[:3],  # Limit to top 3 sources
                "search_metadata": {
                    "search_depth": search_depth,
                    "timestamp": datetime.now().isoformat(),
                    "provider": "Tavily"
                }
            }
            
            if include_raw_content:
                mcp_result["raw_data"] = data
            
            return mcp_result
            
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

class MCPClient:
    """MCP client for interacting with search server"""
    
    def __init__(self):
        self.server = MCPWebSearchServer()
    
    def search(self, query: str, **kwargs) -> Dict:
        """Perform MCP search"""
        message = MCPMessage(
            method="search",
            params={"query": query, **kwargs}
        )
        
        response = self.server.handle_request(message)
        
        if response.error:
            return {"error": response.error["message"]}
        
        return response.result
    
    def get_capabilities(self) -> Dict:
        """Get MCP server capabilities"""
        message = MCPMessage(method="capabilities")
        response = self.server.handle_request(message)
        return response.result
    
    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """Get search history"""
        message = MCPMessage(method="history", params={"limit": limit})
        response = self.server.handle_request(message)
        return response.result.get("history", [])

# Global MCP client instance
mcp_client = MCPClient()
