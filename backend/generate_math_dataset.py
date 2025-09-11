#!/usr/bin/env python3
"""
Generate Mathematics Dataset Questions
This script generates sample mathematical questions based on common topics.
"""

import json
import uuid
import random
import os
from typing import List, Dict

def generate_arithmetic_questions() -> List[Dict]:
    """Generate arithmetic questions"""
    questions = []
    
    # Addition questions
    for i in range(10):
        a, b = random.randint(1, 100), random.randint(1, 100)
        questions.append({
            'id': str(uuid.uuid4()),
            'question': f"What is {a} + {b}?",
            'answer': str(a + b),
            'steps': f"Add {a} and {b} to get {a + b}",
            'topic': 'Arithmetic',
            'subtopic': 'Addition',
            'difficulty': 'easy',
            'source': 'Generated_Mathematics'
        })
    
    # Multiplication questions
    for i in range(10):
        a, b = random.randint(2, 12), random.randint(2, 12)
        questions.append({
            'id': str(uuid.uuid4()),
            'question': f"What is {a} × {b}?",
            'answer': str(a * b),
            'steps': f"Multiply {a} by {b} to get {a * b}",
            'topic': 'Arithmetic',
            'subtopic': 'Multiplication',
            'difficulty': 'easy',
            'source': 'Generated_Mathematics'
        })
    
    return questions

def generate_algebra_questions() -> List[Dict]:
    """Generate algebra questions"""
    questions = []
    
    # Linear equations
    for i in range(15):
        a, b, c = random.randint(1, 10), random.randint(1, 10), random.randint(1, 50)
        # ax + b = c, so x = (c - b) / a
        x = (c - b) / a
        if x == int(x):  # Only integer solutions
            x = int(x)
            questions.append({
                'id': str(uuid.uuid4()),
                'question': f"Solve for x: {a}x + {b} = {c}",
                'answer': str(x),
                'steps': f"1. Subtract {b} from both sides: {a}x = {c - b}\n2. Divide by {a}: x = {x}",
                'topic': 'Algebra',
                'subtopic': 'Linear Equations',
                'difficulty': 'medium',
                'source': 'Generated_Mathematics'
            })
    
    # Quadratic equations (simple factoring)
    roots_pairs = [(1, 2), (1, 3), (2, 3), (1, 4), (2, 4), (1, 5), (3, 4), (2, 5)]
    for r1, r2 in roots_pairs:
        # (x - r1)(x - r2) = x² - (r1+r2)x + r1*r2
        b_coeff = -(r1 + r2)
        c_coeff = r1 * r2
        questions.append({
            'id': str(uuid.uuid4()),
            'question': f"Solve x² {'+' if b_coeff >= 0 else ''}{b_coeff}x + {c_coeff} = 0",
            'answer': f"x = {r1}, x = {r2}",
            'steps': f"Factor as (x - {r1})(x - {r2}) = 0\nSolutions: x = {r1}, x = {r2}",
            'topic': 'Algebra',
            'subtopic': 'Quadratic Equations',
            'difficulty': 'medium',
            'source': 'Generated_Mathematics'
        })
    
    return questions

def generate_calculus_questions() -> List[Dict]:
    """Generate calculus questions"""
    questions = []
    
    # Basic derivatives
    polynomial_examples = [
        ("x²", "2x"),
        ("x³", "3x²"), 
        ("2x²", "4x"),
        ("3x³", "9x²"),
        ("x⁴", "4x³"),
        ("5x²", "10x"),
        ("x² + 3x", "2x + 3"),
        ("2x³ - x²", "6x² - 2x"),
        ("x³ + 2x² - 5x", "3x² + 4x - 5")
    ]
    
    for expr, derivative in polynomial_examples:
        questions.append({
            'id': str(uuid.uuid4()),
            'question': f"Find the derivative of {expr}",
            'answer': derivative,
            'steps': f"Using power rule to differentiate {expr} gives {derivative}",
            'topic': 'Calculus',
            'subtopic': 'Derivatives',
            'difficulty': 'medium',
            'source': 'Generated_Mathematics'
        })
    
    # Basic integrals
    integral_examples = [
        ("x", "x²/2 + C"),
        ("x²", "x³/3 + C"),
        ("2x", "x² + C"),
        ("3x²", "x³ + C"),
        ("x³", "x⁴/4 + C")
    ]
    
    for expr, integral in integral_examples:
        questions.append({
            'id': str(uuid.uuid4()),
            'question': f"Find the integral of {expr}",
            'answer': integral,
            'steps': f"Using power rule for integration: ∫{expr} dx = {integral}",
            'topic': 'Calculus',
            'subtopic': 'Integration',
            'difficulty': 'medium',
            'source': 'Generated_Mathematics'
        })
    
    return questions

def generate_geometry_questions() -> List[Dict]:
    """Generate geometry questions"""
    questions = []
    
    # Area calculations
    rectangle_examples = [(5, 8), (3, 12), (7, 9), (4, 15), (6, 10)]
    for l, w in rectangle_examples:
        area = l * w
        questions.append({
            'id': str(uuid.uuid4()),
            'question': f"What is the area of a rectangle with length {l} and width {w}?",
            'answer': str(area),
            'steps': f"Area = length × width = {l} × {w} = {area}",
            'topic': 'Geometry',
            'subtopic': 'Area',
            'difficulty': 'easy',
            'source': 'Generated_Mathematics'
        })
    
    # Circle areas
    radii = [3, 4, 5, 6, 7, 8, 10]
    for r in radii:
        questions.append({
            'id': str(uuid.uuid4()),
            'question': f"What is the area of a circle with radius {r}?",
            'answer': f"{r}²π" if r != 1 else "π",
            'steps': f"Area = πr² = π × {r}² = {r}²π",
            'topic': 'Geometry',
            'subtopic': 'Circle',
            'difficulty': 'easy',
            'source': 'Generated_Mathematics'
        })
    
    return questions

def generate_probability_questions() -> List[Dict]:
    """Generate probability questions"""
    questions = []
    
    # Coin flip problems
    questions.append({
        'id': str(uuid.uuid4()),
        'question': "What is the probability of getting heads when flipping a fair coin?",
        'answer': "1/2",
        'steps': "There are 2 equally likely outcomes (heads, tails), so P(heads) = 1/2",
        'topic': 'Probability',
        'subtopic': 'Basic Probability',
        'difficulty': 'easy',
        'source': 'Generated_Mathematics'
    })
    
    # Dice problems
    questions.append({
        'id': str(uuid.uuid4()),
        'question': "What is the probability of rolling a 6 on a standard die?",
        'answer': "1/6",
        'steps': "There are 6 equally likely outcomes (1,2,3,4,5,6), so P(6) = 1/6",
        'topic': 'Probability',
        'subtopic': 'Basic Probability',
        'difficulty': 'easy',
        'source': 'Generated_Mathematics'
    })
    
    # Two dice sums
    questions.append({
        'id': str(uuid.uuid4()),
        'question': "What is the probability of getting a sum of 8 when rolling two dice?",
        'answer': "5/36",
        'steps': "Favorable outcomes: (2,6), (3,5), (4,4), (5,3), (6,2) = 5 outcomes\nTotal outcomes: 36\nP(sum=8) = 5/36",
        'topic': 'Probability',
        'subtopic': 'Two Events',
        'difficulty': 'medium',
        'source': 'Generated_Mathematics'
    })
    
    return questions

def generate_math_questions() -> List[Dict]:
    """Generate all mathematics questions"""
    questions = []
    
    print("Generating arithmetic questions...")
    questions.extend(generate_arithmetic_questions())
    
    print("Generating algebra questions...")
    questions.extend(generate_algebra_questions())
    
    print("Generating calculus questions...")
    questions.extend(generate_calculus_questions())
    
    print("Generating geometry questions...")
    questions.extend(generate_geometry_questions())
    
    print("Generating probability questions...")
    questions.extend(generate_probability_questions())
    
    return questions

def normalize_and_save(questions: List[Dict], output_file: str = 'normalized_math.json'):
    """Save normalized questions to JSON file"""
    print(f"Saving {len(questions)} questions to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully saved to {output_file}")

def generate_dataset(num_items: int = 1000) -> List[Dict]:
    """Generate a dataset of a specified size"""
    all_questions = []
    
    # Keep generating until we reach the desired number of items
    while len(all_questions) < num_items:
        all_questions.extend(generate_arithmetic_questions())
        all_questions.extend(generate_algebra_questions())
        all_questions.extend(generate_calculus_questions())
        all_questions.extend(generate_geometry_questions())
        all_questions.extend(generate_probability_questions())
        
        # Break if no new questions are being generated
        if len(all_questions) % 100 == 0:
            print(f"Generated {len(all_questions)} questions...")

    # Shuffle and trim to the exact number of items
    random.shuffle(all_questions)
    return all_questions[:num_items]

def save_dataset(dataset: List[Dict], filename: str):
    """Save the dataset to a JSON file"""
    output_path = os.path.join(os.path.dirname(__file__), filename)
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"✅ Dataset saved to {output_path}")

def main():
    """Main function to generate and save mathematics dataset"""
    print("🧮 Generating Mathematics Dataset Questions...")
    
    # Change to backend directory
    os.chdir('C:\\Math Routing Agent\\backend')
    
    try:
        # Generate questions
        questions = generate_math_questions()  # Generate sample mathematics questions
        
        if not questions:
            print("❌ No questions generated!")
            return
        
        # Save normalized questions
        normalize_and_save(questions)
        
        # Show sample questions
        print("\n📝 Sample generated questions:")
        for i, q in enumerate(questions[:3]):
            print(f"\n{i+1}. Topic: {q['topic']}")
            print(f"   Question: {q['question']}")
            print(f"   Answer: {q['answer']}")
            print(f"   Difficulty: {q['difficulty']}")
        
        print(f"\n✅ Successfully generated {len(questions)} mathematics questions!")
        
    except Exception as e:
        print(f"❌ Error generating mathematics dataset: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Generate and save the dataset
    print("🚀 Starting dataset generation...")
    math_dataset = generate_dataset(num_items=1000)
    save_dataset(math_dataset, "normalized_math.json")
    print(f"🎉 Successfully generated {len(math_dataset)} questions.")
