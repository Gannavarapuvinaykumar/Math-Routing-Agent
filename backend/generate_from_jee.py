import json
import uuid

def generate_dataset(input_file, output_file, num_items):
    """
    Generates a new dataset in the desired format from an existing JSON file.

    Args:
        input_file (str): The path to the input JSON file.
        output_file (str): The path to the output JSON file.
        num_items (int): The number of items to generate.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    new_data = []
    for i, item in enumerate(original_data[:num_items]):
        new_item = {
            "id": item.get("id", str(uuid.uuid4())),
            "question": item.get("question", "N/A"),
            "answer": "Generated Answer",
            "steps": "1. Step 1\n2. Step 2\n3. Step 3",
            "topic": item.get("topic", "math"),
            "subtopic": "Generated Subtopic",
            "difficulty": "medium",
            "source": item.get("source", "Kaggle_JEE")
        }
        new_data.append(new_item)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully generated {len(new_data)} items.")
    print(f"✅ Saved to {output_file}")

if __name__ == "__main__":
    generate_dataset("normalized_jee.json", "normalized_jee_generated.json", 1000)
