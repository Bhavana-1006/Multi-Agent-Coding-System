import os
import sys
import json
import time
from typing import Dict, List, Any

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from execution.pytest_runner import run_tests_in_sandbox
from training.benchmark_loader import load_local_benchmark, get_benchmark_stats

REQUIRED_FIELDS = [
    "task_id", "prompt", "canonical_solution", "test", "entry_point",
    "difficulty", "category", "constraints", "expected_output",
    "edge_cases", "common_errors", "test_cases"
]

BUGGY_REQUIRED_FIELDS = [
    "buggy_solution", "error_type", "buggy_error", "repair_hint", "repaired_solution"
]

VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}
VALID_CATEGORIES = {
    "Arrays", "Strings", "Searching & Sorting", "Dynamic Programming",
    "Trees & Graphs", "Data Structures", "Math", "Recursion", "General Programming"
}

def validate_schema(problems: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validates structural integrity, presence of required keys, and types."""
    errors = []
    buggy_count = 0

    for p in problems:
        tid = p.get("task_id", "UNKNOWN")
        for f in REQUIRED_FIELDS:
            if f not in p or p[f] is None:
                errors.append(f"[{tid}] Missing required field '{f}'")

        if p.get("difficulty") not in VALID_DIFFICULTIES:
            errors.append(f"[{tid}] Invalid difficulty: {p.get('difficulty')}")

        if p.get("category") not in VALID_CATEGORIES:
            errors.append(f"[{tid}] Invalid category: {p.get('category')}")

        if not isinstance(p.get("constraints"), list) or len(p.get("constraints", [])) == 0:
            errors.append(f"[{tid}] 'constraints' must be a non-empty list")

        if not isinstance(p.get("test_cases"), list) or len(p.get("test_cases", [])) == 0:
            errors.append(f"[{tid}] 'test_cases' must be a non-empty list")

        if p.get("has_buggy_solution") or p.get("buggy_solution"):
            buggy_count += 1
            for bf in BUGGY_REQUIRED_FIELDS:
                if bf not in p or not p[bf]:
                    errors.append(f"[{tid}] Missing failure-oriented field '{bf}'")

    return {
        "valid": len(errors) == 0,
        "total_checked": len(problems),
        "buggy_fields_checked": buggy_count,
        "error_count": len(errors),
        "errors": errors[:15]
    }

def validate_solutions_execution(problems: List[Dict[str, Any]], sample_limit: int = None) -> Dict[str, Any]:
    """
    Executes:
    1. Canonical solutions (must pass 100%)
    2. Buggy solutions (must fail 100%)
    3. Repaired solutions (must pass 100%)
    """
    targets = problems[:sample_limit] if sample_limit else problems
    print(f"\n[Execution Validation] Testing {len(targets)} problems in sandbox...")

    canonical_passed = 0
    canonical_failed = []
    
    buggy_attempted = 0
    buggy_correctly_failed = 0
    buggy_unexpected_pass = []
    
    repaired_attempted = 0
    repaired_passed = 0
    repaired_failed = []

    t0 = time.time()

    for idx, p in enumerate(targets, 1):
        tid = p["task_id"]
        test_code = p["test"]
        ep = p.get("entry_point")

        # 1. Canonical Solution Verification
        res_canon = run_tests_in_sandbox(code=p["canonical_solution"], test_code=test_code, timeout=5.0, entry_point=ep)
        if res_canon.passed:
            canonical_passed += 1
        else:
            canonical_failed.append({"task_id": tid, "error": res_canon.stderr or res_canon.stdout})

        # 2. Buggy Solution Verification
        if p.get("buggy_solution"):
            buggy_attempted += 1
            res_buggy = run_tests_in_sandbox(code=p["buggy_solution"], test_code=test_code, timeout=5.0, entry_point=ep)
            if not res_buggy.passed:
                buggy_correctly_failed += 1
            else:
                buggy_unexpected_pass.append(tid)

        # 3. Repaired Solution Verification
        if p.get("repaired_solution"):
            repaired_attempted += 1
            res_repaired = run_tests_in_sandbox(code=p["repaired_solution"], test_code=test_code, timeout=5.0, entry_point=ep)
            if res_repaired.passed:
                repaired_passed += 1
            else:
                repaired_failed.append({"task_id": tid, "error": res_repaired.stderr})

        if idx % 25 == 0 or idx == len(targets):
            print(f"  Processed {idx:3d}/{len(targets)} problems ({canonical_passed}/{idx} canonical solutions verified)")

    total_time = time.time() - t0

    return {
        "total_evaluated": len(targets),
        "execution_time_seconds": total_time,
        "canonical": {
            "total": len(targets),
            "passed": canonical_passed,
            "failed": len(canonical_failed),
            "pass_rate_pct": (canonical_passed / len(targets)) * 100.0 if targets else 0.0,
            "failed_samples": canonical_failed[:5]
        },
        "buggy": {
            "total": buggy_attempted,
            "correctly_failed": buggy_correctly_failed,
            "unexpected_passes": len(buggy_unexpected_pass),
            "detection_rate_pct": (buggy_correctly_failed / buggy_attempted) * 100.0 if buggy_attempted else 100.0,
            "unexpected_pass_ids": buggy_unexpected_pass
        },
        "repaired": {
            "total": repaired_attempted,
            "passed": repaired_passed,
            "failed": len(repaired_failed),
            "pass_rate_pct": (repaired_passed / repaired_attempted) * 100.0 if repaired_attempted else 100.0,
            "failed_samples": repaired_failed[:5]
        }
    }

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logs_dir = os.path.join(root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    print("=" * 70)
    print("      EXTENDED BENCHMARK DATASET: AUTOMATED VALIDATION SUITE      ")
    print("=" * 70)

    # 1. Load full dataset
    problems = load_local_benchmark("all")
    stats = get_benchmark_stats(problems)
    print(f"Loaded {len(problems)} benchmark items across sources: {stats['sources']}")
    print(f"Difficulty breakdown: {stats['difficulties']}")
    print(f"Category breakdown:   {stats['categories']}")

    # 2. Schema Validation
    print("\n--- Running Schema Integrity Checks ---")
    schema_res = validate_schema(problems)
    if schema_res["valid"]:
        print(f"[PASS] 100% Schema Correctness across all {schema_res['total_checked']} problems.")
        print(f"       Verified {schema_res['buggy_fields_checked']} problems with complete failure/repair fields.")
    else:
        print(f"[FAIL] Found {schema_res['error_count']} schema errors:")
        for err in schema_res["errors"]:
            print(f"  - {err}")

    # 3. Execution Verification on Custom Problems & Representative HumanEval Problems
    # Verify all 65 custom problems + 30 buggy HumanEval problems (95 total with full bug pairs)
    eval_subset = [p for p in problems if p.get("source") == "Custom" or p.get("has_buggy_solution")]
    print(f"\n--- Running Execution Sandbox Validation on {len(eval_subset)} Multi-Agent Problems ---")
    exec_res = validate_solutions_execution(eval_subset)

    print("\n" + "=" * 70)
    print("                DATASET VALIDATION EXECUTION SUMMARY                 ")
    print("=" * 70)
    c = exec_res["canonical"]
    b = exec_res["buggy"]
    r = exec_res["repaired"]

    print(f"1. Canonical Solutions Pass Rate: {c['pass_rate_pct']:.1f}% ({c['passed']}/{c['total']})")
    print(f"2. Buggy Solutions Failure Rate:  {b['detection_rate_pct']:.1f}% ({b['correctly_failed']}/{b['total']})")
    print(f"3. Repaired Solutions Pass Rate:  {r['pass_rate_pct']:.1f}% ({r['passed']}/{r['total']})")
    print(f"Total Sandbox Verification Time:  {exec_res['execution_time_seconds']:.2f}s")
    print("=" * 70)

    # Export report to JSON
    report_data = {
        "dataset_stats": stats,
        "schema_validation": schema_res,
        "execution_validation": exec_res,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    report_path = os.path.join(logs_dir, "dataset_validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"\n[Saved] Detailed validation report written to: {report_path}")

if __name__ == "__main__":
    main()
