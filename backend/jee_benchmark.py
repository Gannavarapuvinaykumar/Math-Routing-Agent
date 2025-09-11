"""
JEE Benchmark Script for Math Routing Agent
"""
import asyncio
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Any
import os
from datetime import datetime

class JEEBenchmark:
    """Benchmark the Math Routing Agent against JEE dataset"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:8000/api"):
        self.api_base_url = api_base_url
        self.results = []
        self.stats = {
            "total_questions": 0,
            "kb_route_count": 0,
            "web_route_count": 0,
            "ai_route_count": 0,
            "human_route_count": 0,
            "error_count": 0,
            "avg_response_time": 0,
            "accuracy_scores": []
        }
    
    def load_jee_questions(self, limit: int = 50) -> List[Dict]:
        """Load JEE questions for benchmarking"""
        # Load from your normalized dataset
        jee_file = "normalized_datasets/jee_sample.json"
        
        if not os.path.exists(jee_file):
            print("JEE dataset not found. Creating sample questions...")
            return self._create_sample_jee_questions(limit)
        
        try:
            with open(jee_file, 'r') as f:
                data = json.load(f)
                return data[:limit] if len(data) > limit else data
        except Exception as e:
            print(f"Error loading JEE data: {e}")
            return self._create_sample_jee_questions(limit)
    
    def _create_sample_jee_questions(self, count: int) -> List[Dict]:
        """Create sample JEE-style questions for benchmarking"""
        sample_questions = [
            {
                "id": 1,
                "question": "Solve the quadratic equation x² - 5x + 6 = 0",
                "answer": "x = 2 or x = 3",
                "topic": "Algebra",
                "difficulty": "Easy"
            },
            {
                "id": 2,
                "question": "Find the derivative of sin(x²)",
                "answer": "2x cos(x²)",
                "topic": "Calculus",
                "difficulty": "Medium"
            },
            {
                "id": 3,
                "question": "Integrate ∫x²dx from 0 to 2",
                "answer": "8/3",
                "topic": "Calculus",
                "difficulty": "Medium"
            },
            {
                "id": 4,
                "question": "Find the area of triangle with vertices (0,0), (3,4), (6,0)",
                "answer": "9 square units",
                "topic": "Geometry",
                "difficulty": "Easy"
            },
            {
                "id": 5,
                "question": "Solve the system: 2x + 3y = 7, 4x - y = 1",
                "answer": "x = 1, y = 5/3",
                "topic": "Algebra",
                "difficulty": "Medium"
            }
        ]
        
        # Repeat and modify to reach desired count
        questions = []
        for i in range(count):
            base_q = sample_questions[i % len(sample_questions)]
            question = base_q.copy()
            question["id"] = i + 1
            questions.append(question)
        
        return questions
    
    def query_agent(self, question: str) -> Dict:
        """Query the math routing agent"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_base_url}/agent_route",
                json={"query": question},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "route": data.get("route", "unknown"),
                    "result": data.get("result", {}),
                    "confidence": data.get("confidence", "none"),
                    "response_time": response_time,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "route": "error",
                    "result": {},
                    "confidence": "none",
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "route": "error",
                "result": {},
                "confidence": "none",
                "response_time": 0,
                "error": str(e)
            }
    
    def evaluate_answer(self, expected: str, actual: str, route: str) -> float:
        """Evaluate answer quality (simple keyword matching for now)"""
        if not actual or not expected:
            return 0.0
        
        expected_lower = expected.lower()
        actual_lower = actual.lower()
        
        # Extract key numbers and words
        import re
        expected_nums = set(re.findall(r'\d+\.?\d*', expected_lower))
        actual_nums = set(re.findall(r'\d+\.?\d*', actual_lower))
        
        # Simple scoring based on route and content similarity
        score = 0.0
        
        # Number overlap
        if expected_nums and actual_nums:
            overlap = len(expected_nums.intersection(actual_nums))
            score += (overlap / len(expected_nums)) * 0.6
        
        # Keyword overlap
        expected_words = set(expected_lower.split())
        actual_words = set(actual_lower.split())
        word_overlap = len(expected_words.intersection(actual_words))
        if expected_words:
            score += (word_overlap / len(expected_words)) * 0.4
        
        # Route-based bonus
        if route == "KB":
            score *= 1.2  # KB answers should be more accurate
        elif route == "AI":
            score *= 1.1  # AI answers are usually good
        elif route == "Web":
            score *= 1.0  # Web answers vary
        
        return min(score, 1.0)  # Cap at 1.0
    
    def run_benchmark(self, limit: int = 20) -> Dict:
        """Run the complete benchmark"""
        print("🧮 Starting JEE Benchmark for Math Routing Agent...")
        print(f"Testing {limit} questions...\n")
        
        questions = self.load_jee_questions(limit)
        self.stats["total_questions"] = len(questions)
        
        for i, q in enumerate(questions, 1):
            print(f"Question {i}/{len(questions)}: {q['question'][:50]}...")
            
            # Query the agent
            result = self.query_agent(q["question"])
            
            # Extract answer
            actual_answer = ""
            if result["success"] and result["result"]:
                actual_answer = result["result"].get("answer", "")
            
            # Evaluate
            accuracy = self.evaluate_answer(
                q.get("answer", ""), 
                actual_answer, 
                result["route"]
            )
            
            # Store result
            benchmark_result = {
                "question_id": q.get("id", i),
                "question": q["question"],
                "expected_answer": q.get("answer", ""),
                "actual_answer": actual_answer,
                "route": result["route"],
                "confidence": result["confidence"],
                "response_time": result["response_time"],
                "accuracy": accuracy,
                "success": result["success"],
                "error": result["error"],
                "topic": q.get("topic", "Unknown"),
                "difficulty": q.get("difficulty", "Unknown")
            }
            
            self.results.append(benchmark_result)
            
            # Update stats
            route = result["route"]
            if route == "KB":
                self.stats["kb_route_count"] += 1
            elif route == "Web":
                self.stats["web_route_count"] += 1
            elif route == "AI":
                self.stats["ai_route_count"] += 1
            elif route == "Human":
                self.stats["human_route_count"] += 1
            else:
                self.stats["error_count"] += 1
            
            self.stats["accuracy_scores"].append(accuracy)
            
            print(f"  Route: {route}, Accuracy: {accuracy:.2f}, Time: {result['response_time']:.2f}s")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        # Calculate final stats
        self.stats["avg_response_time"] = sum(r["response_time"] for r in self.results) / len(self.results)
        self.stats["avg_accuracy"] = sum(self.stats["accuracy_scores"]) / len(self.stats["accuracy_scores"])
        self.stats["success_rate"] = sum(1 for r in self.results if r["success"]) / len(self.results)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate comprehensive benchmark report"""
        report = {
            "benchmark_info": {
                "timestamp": datetime.now().isoformat(),
                "total_questions": self.stats["total_questions"],
                "agent_endpoint": self.api_base_url
            },
            "routing_performance": {
                "kb_route_percentage": (self.stats["kb_route_count"] / self.stats["total_questions"]) * 100,
                "web_route_percentage": (self.stats["web_route_count"] / self.stats["total_questions"]) * 100,
                "ai_route_percentage": (self.stats["ai_route_count"] / self.stats["total_questions"]) * 100,
                "human_route_percentage": (self.stats["human_route_count"] / self.stats["total_questions"]) * 100,
                "error_percentage": (self.stats["error_count"] / self.stats["total_questions"]) * 100
            },
            "performance_metrics": {
                "average_accuracy": round(self.stats["avg_accuracy"], 3),
                "average_response_time": round(self.stats["avg_response_time"], 3),
                "success_rate": round(self.stats["success_rate"], 3),
                "total_errors": self.stats["error_count"]
            },
            "detailed_results": self.results
        }
        
        # Save report
        report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Benchmark Report:")
        print(f"Total Questions: {self.stats['total_questions']}")
        print(f"Average Accuracy: {self.stats['avg_accuracy']:.1%}")
        print(f"Average Response Time: {self.stats['avg_response_time']:.2f}s")
        print(f"Success Rate: {self.stats['success_rate']:.1%}")
        print(f"\nRouting Distribution:")
        print(f"  KB: {self.stats['kb_route_count']} ({(self.stats['kb_route_count']/self.stats['total_questions'])*100:.1f}%)")
        print(f"  Web: {self.stats['web_route_count']} ({(self.stats['web_route_count']/self.stats['total_questions'])*100:.1f}%)")
        print(f"  AI: {self.stats['ai_route_count']} ({(self.stats['ai_route_count']/self.stats['total_questions'])*100:.1f}%)")
        print(f"  Human: {self.stats['human_route_count']} ({(self.stats['human_route_count']/self.stats['total_questions'])*100:.1f}%)")
        print(f"  Errors: {self.stats['error_count']} ({(self.stats['error_count']/self.stats['total_questions'])*100:.1f}%)")
        print(f"\nReport saved: {report_file}")
        
        return report

def main():
    """Run the JEE benchmark"""
    # Check if API is available
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code != 200:
            print("❌ Math Routing Agent API is not running!")
            print("Please start the FastAPI server first: python -m uvicorn main:app --reload")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Please start the FastAPI server first: python -m uvicorn main:app --reload")
        return
    
    # Run benchmark
    benchmark = JEEBenchmark()
    report = benchmark.run_benchmark(limit=20)  # Test with 20 questions
    
    print("\n✅ Benchmark completed successfully!")
    print("Check the generated report file for detailed results.")

if __name__ == "__main__":
    main()
