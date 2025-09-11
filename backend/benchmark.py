"""
Benchmarking Script for Human-in-the-Loop Math Routing Agent
Evaluates retrieval and solution accuracy using a JEE Math dataset.
"""
import requests
import json
from typing import List, Dict

# CONFIG
API_URL = "http://localhost:8000/openai/solve"  # Update if needed
DATASET_PATH = "jee_math_dataset.json"           # Place your dataset here

# Load JEE Math dataset (format: [{"question": ..., "answer": ...}, ...])
def load_dataset(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_agent(dataset: List[Dict]) -> Dict:
    correct = 0
    total = len(dataset)
    detailed_results = []
    for item in dataset:
        question = item["question"]
        expected = item["answer"]
        response = requests.post(API_URL, json={"query": question})
        result = response.json()
        agent_answer = result.get("result") or result.get("answer")
        is_correct = str(expected).strip() in str(agent_answer).strip()
        if is_correct:
            correct += 1
        detailed_results.append({
            "question": question,
            "expected": expected,
            "agent_answer": agent_answer,
            "is_correct": is_correct
        })
    accuracy = correct / total if total else 0
    return {
        "accuracy": accuracy,
        "total": total,
        "correct": correct,
        "results": detailed_results
    }

def main():
    dataset = load_dataset(DATASET_PATH)
    results = evaluate_agent(dataset)
    print(f"Benchmark Results: Accuracy = {results['accuracy']*100:.2f}% ({results['correct']}/{results['total']})")
    # Optionally, print detailed results or save to file
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
