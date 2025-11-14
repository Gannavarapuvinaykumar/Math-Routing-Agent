"""
Input and Output Guardrails for Math Routing Agent
"""
import re
from typing import Dict, List, Optional, Tuple
import os

class InputGuardrails:
    """Input content filtering and validation"""
    def __init__(self):
        # AI-based zero-shot classifier
        try:
            from transformers import pipeline
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        except Exception as e:
            self.classifier = None
            print(f"Zero-shot classifier not available: {e}")
        self.allowed_math_keywords = [
            # Strictly math/education terms only
            "solve", "integrate", "differentiate", "limit", "probability", "equation",
            "geometry", "algebra", "calculus", "derivative", "function", "expression",
            "simplify", "expand", "proof", "theorem", "matrix", "vector", "trigonometry",
            "logarithm", "factorial", "permutation", "combination", "step", "value",
            "find", "compute", "explain", "graph", "plot", "math"
        ]
        
        self.forbidden_keywords = [
            "violence", "hate", "illegal", "drugs", "weapon", "bomb", "kill", 
            "suicide", "self-harm", "adult", "sexual", "racist", "discriminatory",
            # Political content
            "election", "politics", "political", "vote", "voting", "candidate", "parliament", "congress",
            "president", "minister", "government", "democracy", "republican", "democrat", "conservative",
            "liberal", "party", "campaign", "ballot", "polling", "constituency", "senator", "governor",
            # Non-educational topics
            "celebrity", "gossip", "entertainment", "movie", "actor", "actress", "singer", "musician",
            "sports", "football", "basketball", "cricket", "tennis", "game", "match", "tournament",
            "stock", "investment", "trading", "cryptocurrency", "bitcoin", "finance", "money", "profit",
            "business", "company", "corporation", "startup", "entrepreneur", "marketing", "sales"
        ]
        
        self.math_symbols = set('^+-*/=()[]{}√∫∑∏∆∇∞π θ α β γ δ ε λ μ σ Φ')
    
    def validate_input(self, query: str) -> Tuple[bool, str]:
        # Quick accept for short/simple math expressions (e.g. "a+b", "2*x+3")
        # This avoids false negatives from the zero-shot classifier on terse inputs.
        try:
            if isinstance(query, str):
                simple_expr_pattern = r'^[\s0-9a-zA-Z\+\-\*\/\^\=\(\)\[\]\{\}\.]+$'
                has_operator = re.search(r'[\+\-\*\/\^=]', query) is not None
                if re.match(simple_expr_pattern, query) and has_operator and len(query) <= 200:
                    return True, "Input validated as simple math expression"
        except Exception:
            # If regex matching fails for any reason, continue to classifier/fallback checks
            pass

        # AI-based guardrail (preferred)
        ALLOWED_LABELS = ["mathematics", "education"]
        FORBIDDEN_LABELS = ["politics", "health", "cybersecurity", "university", "news", "sports", "business", "entertainment", "history", "geography", "science", "technology", "general"]
        if self.classifier:
            try:
                result = self.classifier(query, ALLOWED_LABELS + FORBIDDEN_LABELS)
                top_label = result["labels"][0]
                if top_label not in ALLOWED_LABELS:
                    return False, "I’m designed to focus only on educational mathematics. Could you please ask me a math-related question?"
            except Exception as e:
                print(f"Zero-shot classifier failed: {e}")
                # Fallback to keyword-based guardrail
        """Validate input query against guardrails"""
        if not query or len(query.strip()) == 0:
            return False, "Query cannot be empty"
        
        if len(query) > 1000:
            return False, "Query too long (max 1000 characters)"
        
        # Check for forbidden content
        query_lower = query.lower()
        for forbidden in self.forbidden_keywords:
            if forbidden in query_lower:
                return False, f"Content policy violation: inappropriate content detected"
        
        # Check if it's math/education related
        has_math_keyword = any(kw in query_lower for kw in self.allowed_math_keywords)
        has_math_symbol = any(c in query for c in self.math_symbols)
        # Only allow if math keyword or math symbol is present (numbers alone are NOT enough)
        if not has_math_keyword and not has_math_symbol:
            return False, "I’m designed to focus only on educational mathematics. Could you please ask me a math-related question?"
        
        return True, "Input validated successfully"

class OutputGuardrails:
    """Output content filtering and validation"""
    
    def __init__(self):
        self.max_response_length = 5000
        self.required_sections = ["answer", "steps"]
        self.safety_keywords = [
            "violence", "harmful", "dangerous", "illegal", "inappropriate"
        ]
    
    def validate_output(self, response: Dict) -> Tuple[bool, str, Dict]:
        """Validate and filter output response"""
        try:
            # Check response structure
            if not isinstance(response, dict):
                return False, "Invalid response format", {}
            
            # Safety check on content
            response_text = str(response).lower()
            for safety_kw in self.safety_keywords:
                if safety_kw in response_text:
                    return False, "Safety policy violation in response", {}
            
            # Validate mathematical content
            filtered_response = self._filter_response(response)
            
            # Check response length
            total_length = sum(len(str(v)) for v in filtered_response.values())
            if total_length > self.max_response_length:
                return False, "Response too long", {}
            
            # Add safety disclaimer only for AI-generated content
            source = filtered_response.get("source", "")
            if "AI" in source or "generation" in source.lower() or "model" in source.lower():
                filtered_response["disclaimer"] = "This solution is generated by AI and should be verified by a human expert."
            
            return True, "Output validated successfully", filtered_response
            
        except Exception as e:
            return False, f"Output validation error: {str(e)}", {}
    
    def _filter_response(self, response: Dict) -> Dict:
        """Filter and clean response content"""
        filtered = {}
        
        # Copy safe fields
        safe_fields = ["answer", "steps", "summary", "question", "topic", "subtopic", 
                      "difficulty", "source", "score", "confidence", "explanation"]
        
        for field in safe_fields:
            if field in response:
                value = response[field]
                if isinstance(value, str):
                    # Clean and validate string content
                    cleaned_value = self._clean_text(value)
                    if cleaned_value:
                        filtered[field] = cleaned_value
                else:
                    filtered[field] = value
        
        return filtered
    
    def _clean_text(self, text: str) -> str:
        """Clean and validate text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Ensure mathematical notation is preserved
        # Remove any potential script injections
        cleaned = re.sub(r'<script.*?</script>', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned

class GuardrailsManager:
    """Central manager for all guardrails"""
    
    def __init__(self):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.violation_log = []
    
    def process_request(self, query: str) -> Tuple[bool, str]:
        """Process input request through guardrails"""
        is_valid, message = self.input_guardrails.validate_input(query)
        
        if not is_valid:
            self._log_violation("INPUT", query, message)
        
        return is_valid, message
    
    def process_response(self, response: Dict) -> Tuple[bool, str, Dict]:
        """Process output response through guardrails"""
        is_valid, message, filtered_response = self.output_guardrails.validate_output(response)
        
        if not is_valid:
            self._log_violation("OUTPUT", str(response), message)
        
        return is_valid, message, filtered_response
    
    def _log_violation(self, violation_type: str, content: str, reason: str):
        """Log guardrail violations"""
        from datetime import datetime
        
        violation = {
            "timestamp": datetime.now().isoformat(),
            "type": violation_type,
            "content": content[:100] + "..." if len(content) > 100 else content,
            "reason": reason
        }
        
        self.violation_log.append(violation)
        
        # Keep only last 100 violations
        if len(self.violation_log) > 100:
            self.violation_log = self.violation_log[-100:]
    
    def get_violation_stats(self) -> Dict:
        """Get guardrail violation statistics"""
        total_violations = len(self.violation_log)
        input_violations = sum(1 for v in self.violation_log if v["type"] == "INPUT")
        output_violations = sum(1 for v in self.violation_log if v["type"] == "OUTPUT")
        
        return {
            "total_violations": total_violations,
            "input_violations": input_violations,
            "output_violations": output_violations,
            "recent_violations": self.violation_log[-5:] if self.violation_log else []
        }

# Global guardrails manager instance
guardrails = GuardrailsManager()
