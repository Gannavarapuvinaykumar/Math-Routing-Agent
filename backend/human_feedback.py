"""
Human-in-the-Loop Feedback System using DSPy
"""
import dspy
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class FeedbackSignature(dspy.Signature):
    """Signature for processing human feedback on math solutions"""
    original_query = dspy.InputField(desc="The original math question")
    ai_solution = dspy.InputField(desc="The AI-generated solution")
    human_feedback = dspy.InputField(desc="Human feedback on the solution")
    improved_solution = dspy.OutputField(desc="Improved solution based on feedback")

class FeedbackProcessor(dspy.Module):
    """DSPy module for processing human feedback"""
    
    def __init__(self):
        super().__init__()
        self.feedback_chain = dspy.ChainOfThought(FeedbackSignature)
        
    def forward(self, original_query, ai_solution, human_feedback):
        return self.feedback_chain(
            original_query=original_query,
            ai_solution=ai_solution,
            human_feedback=human_feedback
        )

class HumanFeedbackSystem:
    def store_in_kb(self, query: str, answer: str, steps: str = None, topic: str = None, subtopic: str = None, difficulty: str = None, source: str = "Human Feedback"):
        """Store validated/corrected Q&A pair in Qdrant KB"""
        try:
            from sentence_transformers import SentenceTransformer
            from qdrant_client import QdrantClient
            import os
            model = SentenceTransformer(os.getenv('EMBED_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'))
            client = QdrantClient(host=os.getenv('QDRANT_HOST', 'localhost'), port=int(os.getenv('QDRANT_PORT', 6333)))
            query_vec = model.encode(query).tolist()
            payload = {
                "question": query,
                "answer": answer,
                "steps": steps,
                "topic": topic,
                "subtopic": subtopic,
                "difficulty": difficulty,
                "source": source
            }
            client.upsert(
                collection_name=os.getenv('COLLECTION_NAME', 'math_kb'),
                points=[{
                    "id": int(datetime.now().timestamp() * 1000),
                    "vector": query_vec,
                    "payload": payload
                }]
            )
            print(f"Stored validated answer in KB: {query}")
        except Exception as e:
            print(f"Error storing in KB: {e}")
    """Human-in-the-Loop feedback and learning system"""
    
    def __init__(self):
        self.feedback_db_path = "feedback_database.json"
        self.feedback_processor = FeedbackProcessor()
        self.load_feedback_database()
        
    def load_feedback_database(self):
        """Load existing feedback data"""
        try:
            if os.path.exists(self.feedback_db_path):
                with open(self.feedback_db_path, 'r') as f:
                    self.feedback_data = json.load(f)
            else:
                self.feedback_data = {"feedback_entries": [], "stats": {"total_feedback": 0}}
        except Exception as e:
            print(f"Error loading feedback database: {e}")
            self.feedback_data = {"feedback_entries": [], "stats": {"total_feedback": 0}}
    
    def save_feedback_database(self):
        """Save feedback data to file"""
        try:
            with open(self.feedback_db_path, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"Error saving feedback database: {e}")
    
    def submit_feedback(self, query: str, ai_solution: str, human_feedback: str, rating: int) -> Dict:
        """Submit human feedback for a solution"""
        try:
            # Process feedback using DSPy
            improved = self.feedback_processor.forward(
                original_query=query,
                ai_solution=ai_solution,
                human_feedback=human_feedback
            )
            # Store feedback entry
            feedback_entry = {
                "id": len(self.feedback_data["feedback_entries"]) + 1,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "ai_solution": ai_solution,
                "human_feedback": human_feedback,
                "rating": rating,
                "improved_solution": improved.improved_solution,
                "status": "processed"
            }
            self.feedback_data["feedback_entries"].append(feedback_entry)
            self.feedback_data["stats"]["total_feedback"] += 1
            self.save_feedback_database()
            # If feedback is positive or contains a correction, store in KB
            if rating >= 4 or (human_feedback and human_feedback.strip()):
                self.store_in_kb(
                    query=query,
                    answer=improved.improved_solution or ai_solution,
                    steps=None,
                    topic=None,
                    subtopic=None,
                    difficulty=None,
                    source="Human Feedback"
                )
            return {
                "success": True,
                "feedback_id": feedback_entry["id"],
                "improved_solution": improved.improved_solution,
                "message": "Feedback processed and stored successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process feedback"
            }
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        entries = self.feedback_data["feedback_entries"]
        if not entries:
            return {"total_feedback": 0, "average_rating": 0, "recent_feedback": []}
        ratings = [entry["rating"] for entry in entries if "rating" in entry]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        recent_feedback = entries[-5:] if len(entries) >= 5 else entries
        return {
            "total_feedback": len(entries),
            "average_rating": round(avg_rating, 2),
            "recent_feedback": recent_feedback
        }

    def require_human_feedback(self, query: str) -> Dict:
        """Generate message for queries requiring human feedback"""
        return {
            "message": f"This complex query requires human expertise: '{query}'",
            "explanation": "Our automated systems (Knowledge Base, Web Search, and AI) could not provide a satisfactory answer.",
            "action_required": "Please provide feedback to help improve our system",
            "feedback_form": {
                "query": query,
                "rating_scale": "1-5 (1=Poor, 5=Excellent)",
                "feedback_prompt": "Please provide your solution or feedback"
            }
        }

# Global feedback system instance
feedback_system = HumanFeedbackSystem()
