# Math Routing Agent: Dataset Normalization Script
# This script will normalize DeepMind MATH and JEE datasets to the required format.
# Usage: python normalize_datasets.py

import json
import os
from typing import List, Dict


# Normalization function for richer schema
import uuid

def normalize_math_dataset(input_path: str, output_path: str, source_name: str, topics_priority=None):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    normalized = []
    # If data is a dict (topic: list of questions), flatten it
    if isinstance(data, dict):
        for topic, items in data.items():
            for item in items:
                # If item is a string, skip or wrap as needed
                if isinstance(item, str):
                    continue
                normalized.append({
                    'id': str(uuid.uuid4()),
                    'question': item.get('question'),
                    'answer': item.get('answer'),
                    'steps': item.get('steps', ''),
                    'topic': topic,
                    'subtopic': item.get('subtopic', ''),
                    'difficulty': item.get('difficulty', 'Unknown'),
                    'source': source_name
                })
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                continue
            topic = item.get('topic', 'Unknown')
            normalized.append({
                'id': str(uuid.uuid4()),
                'question': item.get('question'),
                'answer': item.get('answer'),
                'steps': item.get('steps', ''),
                'topic': topic,
                'subtopic': item.get('subtopic', ''),
                'difficulty': item.get('difficulty', 'Unknown'),
                'source': source_name
            })
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Prioritize these topics for demo
    topics_priority = [
        'Algebra', 'Calculus', 'Coordinate Geometry', 'Arithmetic', 'Probability'
    ]
    # Example usage (update paths as needed)
    normalize_math_dataset('JEE/jee.json', 'normalized_jee.json', 'Kaggle_JEE', topics_priority)
    
    # Generate and process mathematics dataset
    print("Generating mathematics dataset...")
    import subprocess
    result = subprocess.run(['python', 'generate_math_dataset.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Mathematics dataset generated successfully")
    else:
        print(f"❌ Error generating mathematics dataset: {result.stderr}")
