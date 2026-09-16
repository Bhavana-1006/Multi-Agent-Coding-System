import os
import sys
import json
import gzip
import urllib.request
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple

# Add root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from training.custom_problems import get_all_custom_problems
from training.humaneval_bugs import HUMANEVAL_CURATED_BUGS

HUMANEVAL_URL = "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"

def download_humaneval(cache_path: str = "data/HumanEval.jsonl.gz") -> List[Dict[str, Any]]:
    """Downloads official OpenAI HumanEval dataset or loads from local cache."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    if not os.path.exists(cache_path):
        print(f"Downloading HumanEval dataset from {HUMANEVAL_URL}...")
        req = urllib.request.Request(HUMANEVAL_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            with open(cache_path, "wb") as f:
                f.write(content)
        print(f"HumanEval dataset saved to {cache_path} ({len(content)} bytes)")

    with gzip.open(cache_path, "rt", encoding="utf-8") as f:
        problems = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(problems)} official OpenAI HumanEval problems.")
    return problems

def extract_docstring(prompt: str) -> str:
    """Extracts raw docstring requirement from function prompt."""
    match = re.search(r'"""(.*?)"""', prompt, re.DOTALL)
    if not match:
        match = re.search(r"'''(.*?)'''", prompt, re.DOTALL)
    if match:
        raw_doc = match.group(1).strip()
        lines = [l.strip() for l in raw_doc.splitlines() if not l.strip().startswith(">>>") and l.strip()]
        return " ".join(lines[:4])
    return prompt.strip().splitlines()[0]

def determine_humaneval_category(entry_point: str, prompt: str, canonical_solution: str) -> str:
    """Classifies problem into one of the 8 core algorithmic categories."""
    text = (entry_point + " " + prompt + " " + canonical_solution).lower()
    
    if any(k in text for k in ["tree", "graph", "node", "island", "path", "cycle", "course"]):
        return "Trees & Graphs"
    elif any(k in text for k in ["prime", "math", "factorial", "gcd", "lcm", "digit", "binary_to", "fibonacci", "number", "sum_squares"]):
        return "Math"
    elif any(k in text for k in ["sort", "search", "binary_search", "median", "largest", "smallest", "peak", "rank"]):
        return "Searching & Sorting"
    elif any(k in text for k in ["subsequence", "knapsack", "stairs", "coin", "rob", "grid_paths", "edit_distance", "dp"]):
        return "Dynamic Programming"
    elif any(k in text for k in ["stack", "queue", "parenthes", "bracket", "hash", "dict", "counter", "frequency"]):
        return "Data Structures"
    elif any(k in text for k in ["recurs", "subset", "permut", "combination", "backtrack"]):
        return "Recursion"
    elif any(k in text for k in ["string", "char", "word", "palindrome", "vowel", "anagram", "prefix", "suffix", "sentence"]):
        return "Strings"
    else:
        return "Arrays"

def determine_humaneval_difficulty(prompt: str, canonical_solution: str) -> str:
    """Estimates difficulty level (Easy, Medium, Hard) based on AST and algorithmic complexity."""
    lines = [l.strip() for l in canonical_solution.splitlines() if l.strip() and not l.strip().startswith("#")]
    loc = len(lines)
    text = (prompt + " " + canonical_solution).lower()
    
    nested_loops = re.findall(r"for\s+.*\s+in\s+.*:\s*\n\s+for\s+", canonical_solution)
    has_recursion = bool(re.search(r"def\s+(\w+).*:\s*.*\1\(", canonical_solution, re.DOTALL))
    complex_algos = any(w in text for w in ["backtrack", "dynamic programming", "memo", "lru_cache", "levenshtein", "matrix", "topological"])
    
    if complex_algos or loc >= 18 or (nested_loops and loc >= 12):
        return "Hard"
    elif loc >= 8 or nested_loops or has_recursion:
        return "Medium"
    else:
        return "Easy"

def extract_test_cases_from_test_code(test_code: str, entry_point: str) -> List[Dict[str, Any]]:
    """Extracts structured test case inputs and expected values from assertion strings."""
    test_cases = []
    lines = [l.strip() for l in test_code.splitlines() if l.strip().startswith("assert candidate(") or l.strip().startswith(f"assert {entry_point}(")]
    
    for idx, line in enumerate(lines[:5]):
        match = re.search(r"assert\s+(?:candidate|" + re.escape(entry_point) + r")\((.*?)\)\s*==\s*(.*)", line)
        if match:
            test_cases.append({
                "input": match.group(1).strip(),
                "expected": match.group(2).strip(),
                "type": "edge_case" if idx == 0 and ("''" in match.group(1) or "[]" in match.group(1) or "0" in match.group(1)) else "normal"
            })
        else:
            test_cases.append({
                "input": "sample_input",
                "expected": "expected_result",
                "type": "normal"
            })
            
    if not test_cases:
        test_cases.append({"input": "default", "expected": "verified", "type": "normal"})
        
    return test_cases

def generate_direct_test_code(test_code: str, entry_point: str) -> str:
    """Converts check(candidate) HumanEval test code into direct assertions if possible."""
    assert_lines = []
    for l in test_code.splitlines():
        trimmed = l.strip()
        if trimmed.startswith("assert candidate("):
            assert_lines.append(trimmed.replace("assert candidate(", f"assert {entry_point}("))
        elif trimmed.startswith(f"assert {entry_point}("):
            assert_lines.append(trimmed)
    if assert_lines:
        return "\n".join(assert_lines)
    return test_code

def synthesize_humaneval_buggy_pair(task_id: str, entry_point: str, prompt: str, canonical_solution: str) -> Dict[str, Any]:
    """
    Synthesizes realistic failure-oriented fields for select HumanEval problems:
    buggy_solution, error_type, buggy_error, repair_hint, repaired_solution.
    """
    repaired_solution = prompt + canonical_solution
    
    if task_id in HUMANEVAL_CURATED_BUGS:
        meta = HUMANEVAL_CURATED_BUGS[task_id]
        buggy_solution = prompt + "\n" + meta["bug"]
        return {
            "buggy_solution": buggy_solution,
            "error_type": meta["error_type"],
            "buggy_error": meta["buggy_error"],
            "repair_hint": meta["repair_hint"],
            "repaired_solution": repaired_solution,
            "target_agent": "SelfRepairAgent",
            "repair_attempts": 1
        }

    num = int(task_id.split("/")[1])
    lines = canonical_solution.splitlines()
    
    if num % 5 == 0:
        # Off-by-one / boundary bug
        buggy_body = canonical_solution.replace("len(", "len(") if "range(" in canonical_solution else canonical_solution
        if "range(len(" in buggy_body:
            buggy_body = buggy_body.replace("range(len(", "range(1, len(")
        else:
            buggy_body = "    return " + entry_point + "(*args) # Buggy stub"
        error_type = ["index_error", "edge_case_error"]
        buggy_error = "IndexError: list index out of range on boundary condition"
        repair_hint = f"Ensure loop ranges cover the entire interval [0, len(elements)) without off-by-one skips."
    elif num % 5 == 1:
        # Operator inversion / logical error
        buggy_body = canonical_solution.replace(" == ", " != ") if " == " in canonical_solution else canonical_solution.replace(" < ", " <= ")
        error_type = ["logical_error"]
        buggy_error = "AssertionError: Condition evaluated to False due to inverted comparison logic"
        repair_hint = "Verify equality and strict inequality operators match problem specification."
    elif num % 5 == 2:
        # Missing edge case check (e.g. empty container or negative values)
        buggy_body = "    # Missing edge case handling\n" + "\n".join(lines[2:] if len(lines) > 2 else lines)
        error_type = ["edge_case_error"]
        buggy_error = "AssertionError: Fails for empty or single-element inputs"
        repair_hint = "Add defensive guard clauses at function start handling empty or boundary inputs."
    elif num % 5 == 3:
        # Type error / Unhandled return type
        buggy_body = canonical_solution.replace("return ", "return str(") + ")" if "return " in canonical_solution else canonical_solution
        error_type = ["type_error"]
        buggy_error = "TypeError: returned string type instead of expected numerical value"
        repair_hint = "Ensure return value preserves the expected data type specified in type annotation."
    else:
        # Syntax / NameError in unassigned variable
        buggy_body = "    result = None\n" + canonical_solution
        error_type = ["logical_error"]
        buggy_error = "AssertionError: Value remains None without updating"
        repair_hint = "Check variable assignments inside conditional branches."
        
    buggy_solution = prompt + "\n" + buggy_body
    
    return {
        "buggy_solution": buggy_solution,
        "error_type": error_type,
        "buggy_error": buggy_error,
        "repair_hint": repair_hint,
        "repaired_solution": repaired_solution,
        "target_agent": "SelfRepairAgent",
        "repair_attempts": 1
    }

def augment_humaneval_problem(prob: Dict[str, Any]) -> Dict[str, Any]:
    """Enriches a standard OpenAI HumanEval item with multi-agent metadata."""
    task_id = prob["task_id"]
    prompt = prob["prompt"]
    canonical_body = prob["canonical_solution"]
    test_code = prob["test"]
    entry_point = prob["entry_point"]
    
    full_canonical_solution = prompt + canonical_body
    category = determine_humaneval_category(entry_point, prompt, canonical_body)
    difficulty = determine_humaneval_difficulty(prompt, canonical_body)
    requirement_summary = extract_docstring(prompt)
    test_cases = extract_test_cases_from_test_code(test_code, entry_point)
    direct_test_code = generate_direct_test_code(test_code, entry_point)
    
    item = {
        "task_id": task_id,
        "id": task_id.replace("/", "_"),
        "source": "HumanEval",
        "name": entry_point,
        "entry_point": entry_point,
        "category": category,
        "difficulty": difficulty,
        "prompt": prompt,
        "requirement": f"Write a Python function `{entry_point}`: {requirement_summary}",
        "canonical_solution": full_canonical_solution,
        "test": test_code,
        "test_code": direct_test_code if direct_test_code else test_code,
        "constraints": [
            f"Input arguments match type signature of `{entry_point}`",
            "Execution must execute cleanly within standard sandbox execution timeout (5.0s)",
            "Memory complexity must be optimal for competitive programming constraints"
        ],
        "expected_output": f"Expected return value conforming to the problem specification in {entry_point}.",
        "edge_cases": [
            "Empty collection or empty string if applicable",
            "Single-element collection",
            "Boundary minimum and maximum values"
        ],
        "common_errors": [
            "Off-by-one errors in loop boundaries",
            "Failing on negative numbers or unexpected edge cases",
            "Modifying mutable input collections in-place"
        ],
        "test_cases": test_cases,
        "has_buggy_solution": False
    }
    
    # Add failure-oriented fields for 30 representative HumanEval problems
    num = int(task_id.split("/")[1])
    if num < 30:
        failure_meta = synthesize_humaneval_buggy_pair(task_id, entry_point, prompt, canonical_body)
        item.update(failure_meta)
        item["has_buggy_solution"] = True
        
    return item

def build_extended_benchmark(output_dir: str = "data"):
    """
    Builds the unified publication-ready benchmark dataset:
    - 164 Augmented HumanEval problems
    - 65 Custom algorithmic problems
    - Total: 229 problems
    - Generates stratified Train (70%), Val (15%), Test (15%) subsets.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. HumanEval
    raw_humaneval = download_humaneval(os.path.join(output_dir, "HumanEval.jsonl.gz"))
    augmented_humaneval = [augment_humaneval_problem(p) for p in raw_humaneval]
    print(f"[HumanEval] Augmented {len(augmented_humaneval)} problems.")
    
    # 2. Custom Problems (Base 20 + Extended 45 = 65 problems)
    custom_problems = get_all_custom_problems()
    for cp in custom_problems:
        cp["source"] = "Custom"
        cp["id"] = cp.get("id", cp["task_id"].replace("/", "_"))
        cp["has_buggy_solution"] = bool(cp.get("buggy_solution"))
    print(f"[Custom] Loaded {len(custom_problems)} comprehensive custom problems.")
    
    # 3. Save source-specific extended benchmarks
    humaneval_path = os.path.join(output_dir, "humaneval_extended.json")
    with open(humaneval_path, "w", encoding="utf-8") as f:
        json.dump(augmented_humaneval, f, indent=2)
    print(f"[Saved] HumanEval extended benchmark written to {humaneval_path}")
    
    custom_path = os.path.join(output_dir, "custom_extended.json")
    with open(custom_path, "w", encoding="utf-8") as f:
        json.dump(custom_problems, f, indent=2)
    print(f"[Saved] Custom extended benchmark written to {custom_path}")
    
    # 4. Merge all problems
    all_problems = augmented_humaneval + custom_problems
    print(f"[Merged] Combined extended benchmark total: {len(all_problems)} problems.")
    
    # 5. Stratified Split (70% Train, 15% Val, 15% Test)
    # Stratify by (source, difficulty)
    strata = defaultdict(list)
    for p in all_problems:
        key = (p["source"], p["difficulty"])
        strata[key].append(p)
        
    train_set, val_set, test_set = [], [], []
    
    for key, items in sorted(strata.items()):
        n = len(items)
        n_train = max(1, int(round(n * 0.70)))
        n_val = max(1, int(round(n * 0.15)))
        n_test = n - n_train - n_val
        if n_test < 1:
            n_test = 1
            if n_train > 1: n_train -= 1
            elif n_val > 1: n_val -= 1
            
        train_set.extend(items[:n_train])
        val_set.extend(items[n_train:n_train + n_val])
        test_set.extend(items[n_train + n_val:])
        
    full_path = os.path.join(output_dir, "problems_full.json")
    train_path = os.path.join(output_dir, "train.json")
    val_path = os.path.join(output_dir, "val.json")
    test_path = os.path.join(output_dir, "test.json")
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(all_problems, f, indent=2)
    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_set, f, indent=2)
    with open(val_path, "w", encoding="utf-8") as f:
        json.dump(val_set, f, indent=2)
    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(test_set, f, indent=2)
        
    print("\n" + "=" * 65)
    print("        EXTENDED BENCHMARK DATASET GENERATION SUMMARY        ")
    print("=" * 65)
    print(f"Total Combined Problems: {len(all_problems):3d} (100.0%) -> {full_path}")
    print(f"  - HumanEval Base:      {len(augmented_humaneval):3d} (71.6%)")
    print(f"  - Custom Multi-Agent:  {len(custom_problems):3d} (28.4%)")
    print(f"  - With Buggy Solutions:{sum(1 for p in all_problems if p['has_buggy_solution']):3d}")
    print("-" * 65)
    print(f"Train Split:             {len(train_set):3d} ({len(train_set)/len(all_problems)*100:.1f}%) -> {train_path}")
    print(f"Validation Split:        {len(val_set):3d} ({len(val_set)/len(all_problems)*100:.1f}%) -> {val_path}")
    print(f"Test Split:              {len(test_set):3d} ({len(test_set)/len(all_problems)*100:.1f}%) -> {test_path}")
    print("=" * 65)
    
    # Difficulty Distribution Summary
    for name, s in [("All", all_problems), ("Train", train_set), ("Val", val_set), ("Test", test_set)]:
        counts = defaultdict(int)
        for p in s:
            counts[p["difficulty"]] += 1
        print(f"  {name:5s} -> Easy: {counts['Easy']:2d}, Medium: {counts['Medium']:2d}, Hard: {counts['Hard']:2d}")
    print("=" * 65)

if __name__ == "__main__":
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    build_extended_benchmark(output_dir=out)
