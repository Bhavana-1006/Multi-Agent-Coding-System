import os
import json
from collections import defaultdict
from typing import Dict, List

def split_dataset(
    input_file: str = "data/problems_full.json",
    output_dir: str = "data",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
):
    """
    Partitions the full benchmark problem pool into stratified Train (70%),
    Validation (15%), and Test (15%) subsets based on problem difficulty.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input benchmark file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        problems: List[Dict] = json.load(f)

    print(f"Loaded {len(problems)} benchmark problems from {input_file}")

    # Group by difficulty for stratified splitting
    by_difficulty = defaultdict(list)
    for p in problems:
        diff = p.get("difficulty", "Medium")
        by_difficulty[diff].append(p)

    train_set, val_set, test_set = [], [], []

    # Stratified allocation ensuring every split has Easy, Medium, and Hard
    # For 9 Easy -> 7 Train, 1 Val, 1 Test
    # For 8 Medium -> 6 Train, 1 Val, 1 Test
    # For 3 Hard -> 1 Train, 1 Val, 1 Test
    # Totals: Train=14 (70%), Val=3 (15%), Test=3 (15%)
    for diff, items in by_difficulty.items():
        n = len(items)
        if diff == "Easy":
            n_train, n_val, n_test = 7, 1, 1
        elif diff == "Medium":
            n_train, n_val, n_test = 6, 1, 1
        elif diff == "Hard":
            n_train, n_val, n_test = 1, 1, 1
        else:
            n_train = int(round(n * train_ratio))
            n_val = int(round(n * val_ratio))
            n_test = n - n_train - n_val

        train_set.extend(items[:n_train])
        val_set.extend(items[n_train:n_train + n_val])
        test_set.extend(items[n_train + n_val:])

    os.makedirs(output_dir, exist_ok=True)

    train_path = os.path.join(output_dir, "train.json")
    val_path = os.path.join(output_dir, "val.json")
    test_path = os.path.join(output_dir, "test.json")

    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_set, f, indent=2)
    with open(val_path, "w", encoding="utf-8") as f:
        json.dump(val_set, f, indent=2)
    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(test_set, f, indent=2)

    print("\nDataset Split Summary:")
    print("-" * 50)
    print(f"Train Set:      {len(train_set):2d} problems ({len(train_set)/len(problems)*100:.1f}%) -> {train_path}")
    print(f"Validation Set: {len(val_set):2d} problems ({len(val_set)/len(problems)*100:.1f}%) -> {val_path}")
    print(f"Test Set:       {len(test_set):2d} problems ({len(test_set)/len(problems)*100:.1f}%) -> {test_path}")
    print("-" * 50)

    # Print difficulty distribution
    for name, s in [("Train", train_set), ("Val", val_set), ("Test", test_set)]:
        counts = defaultdict(int)
        for p in s:
            counts[p["difficulty"]] += 1
        print(f"  {name:5s} -> Easy: {counts['Easy']}, Medium: {counts['Medium']}, Hard: {counts['Hard']}")

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_json = os.path.join(project_root, "data", "problems_full.json")
    out_dir = os.path.join(project_root, "data")
    split_dataset(input_file=input_json, output_dir=out_dir)
