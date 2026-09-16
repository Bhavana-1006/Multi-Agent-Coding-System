import os
import json
import urllib.request
from typing import List, Dict

HUMANEVAL_URL = "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"

def load_local_benchmark(split: str = "all", source: str = "all") -> List[Dict]:
    """
    Loads benchmark problems from data/ splits ("all", "train", "val", "test")
    optionally filtered by source ("all", "humaneval", "custom").
    """
    split_map = {
        "all": "problems_full.json",
        "train": "train.json",
        "val": "val.json",
        "test": "test.json",
    }
    target_filename = split_map.get(split.lower(), "problems_full.json")
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    split_path = os.path.join(data_dir, target_filename)

    problems = []
    if os.path.exists(split_path):
        with open(split_path, "r", encoding="utf-8") as f:
            problems = json.load(f)
    else:
        sample_path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_requirements.json")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                problems = json.load(f)

    if source.lower() == "humaneval":
        return [p for p in problems if p.get("source", "").lower() == "humaneval" or "humaneval" in p.get("task_id", "").lower()]
    elif source.lower() == "custom":
        return [p for p in problems if p.get("source", "").lower() == "custom" or "custom" in p.get("task_id", "").lower()]
    return problems

def get_benchmark_stats(problems: List[Dict]) -> Dict:
    """Computes category, difficulty, source, and failure metadata breakdown."""
    stats = {
        "total": len(problems),
        "categories": {},
        "difficulties": {},
        "sources": {},
        "buggy_solutions_count": 0
    }
    for p in problems:
        cat = p.get("category", "General")
        diff = p.get("difficulty", "Unspecified")
        src = p.get("source", "Unknown")
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        stats["difficulties"][diff] = stats["difficulties"].get(diff, 0) + 1
        stats["sources"][src] = stats["sources"].get(src, 0) + 1
        if p.get("has_buggy_solution") or p.get("buggy_solution"):
            stats["buggy_solutions_count"] += 1
    return stats

if __name__ == "__main__":
    for split_name in ["all", "train", "val", "test"]:
        p_list = load_local_benchmark(split=split_name)
        stats = get_benchmark_stats(p_list)
        print(f"[{split_name.upper():5s}] Loaded {len(p_list):3d} problems | Sources: {stats['sources']} | Difficulties: {stats['difficulties']}")

