import os
import sys
import json
import time
from typing import Dict, List, Any
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stable_baselines3 import PPO
from training.benchmark_loader import load_local_benchmark, get_benchmark_stats
from orchestrator.deterministic_router import DeterministicRouter
from orchestrator.rl_orchestrator import MultiAgentCodingEnv

def calculate_dataset_metrics() -> Dict[str, Any]:
    full_problems = load_local_benchmark("all")
    train_problems = load_local_benchmark("train")
    val_problems = load_local_benchmark("val")
    test_problems = load_local_benchmark("test")

    return {
        "total_problems": len(full_problems),
        "train_count": len(train_problems),
        "val_count": len(val_problems),
        "test_count": len(test_problems),
        "full_stats": get_benchmark_stats(full_problems),
        "train_stats": get_benchmark_stats(train_problems),
        "val_stats": get_benchmark_stats(val_problems),
        "test_stats": get_benchmark_stats(test_problems),
    }

def evaluate_rl_simulated(problems: List[Dict[str, Any]], model_path: str) -> Dict[str, Any]:
    if not os.path.exists(model_path):
        return {"error": f"Model not found at {model_path}"}

    model = PPO.load(model_path)
    env = MultiAgentCodingEnv(problems=problems, max_steps=8, simulated=True)
    results = []

    for prob in problems:
        obs, info = env.reset(options={"problem": prob})
        done = False
        step = 0
        total_rew = 0.0
        trajectory = []

        while not done and step < 8:
            action_mask = env.get_action_mask()
            action, _ = model.predict(obs, deterministic=True)
            action = int(action)
            if not action_mask[action]:
                action = int(np.where(action_mask)[0][0])

            trajectory.append(env.ACTION_MAP[action])
            obs, reward, terminated, truncated, info = env.step(action)
            total_rew += reward
            done = terminated or truncated
            step += 1

        state = env.current_state
        passed = bool(state.test_result and state.test_result.passed)
        results.append({
            "id": prob["id"],
            "difficulty": prob.get("difficulty", "Medium"),
            "category": prob.get("category", "General"),
            "passed": passed,
            "steps": len(trajectory),
            "reward": total_rew,
            "trajectory": trajectory
        })

    passed_count = sum(1 for r in results if r["passed"])
    accuracy = (passed_count / len(results)) * 100.0 if results else 0.0
    mean_steps = float(np.mean([r["steps"] for r in results]))
    mean_reward = float(np.mean([r["reward"] for r in results]))

    # Stratified breakdown by difficulty
    diff_stats = {}
    for d in ["Easy", "Medium", "Hard"]:
        sub = [r for r in results if r.get("difficulty") == d]
        if sub:
            p_cnt = sum(1 for r in sub if r["passed"])
            diff_stats[d] = {
                "total": len(sub),
                "passed": p_cnt,
                "accuracy_pct": (p_cnt / len(sub)) * 100.0,
                "mean_steps": float(np.mean([r["steps"] for r in sub])),
                "mean_reward": float(np.mean([r["reward"] for r in sub]))
            }

    # Stratified breakdown by category
    cat_stats = {}
    all_cats = sorted(list({r.get("category", "General") for r in results}))
    for cat in all_cats:
        sub = [r for r in results if r.get("category") == cat]
        if sub:
            p_cnt = sum(1 for r in sub if r["passed"])
            cat_stats[cat] = {
                "total": len(sub),
                "passed": p_cnt,
                "accuracy_pct": (p_cnt / len(sub)) * 100.0,
                "mean_steps": float(np.mean([r["steps"] for r in sub]))
            }

    return {
        "accuracy_pct": accuracy,
        "total_evaluated": len(results),
        "passed_count": passed_count,
        "mean_steps": mean_steps,
        "mean_reward": mean_reward,
        "difficulty_breakdown": diff_stats,
        "category_breakdown": cat_stats,
        "results": results
    }

def evaluate_live_comparison(problems: List[Dict[str, Any]], model_path: str, max_samples: int = 4) -> Dict[str, Any]:
    # Select representative holdout subset across difficulties (1 Easy, 2 Medium, 1 Hard)
    if len(problems) > max_samples:
        easy_probs = [p for p in problems if p.get("difficulty") == "Easy"]
        med_probs = [p for p in problems if p.get("difficulty") == "Medium"]
        hard_probs = [p for p in problems if p.get("difficulty") == "Hard"]
        
        sample_probs = []
        if easy_probs: sample_probs.append(easy_probs[0])
        if med_probs: sample_probs.extend(med_probs[:2])
        if hard_probs: sample_probs.append(hard_probs[0])
        if len(sample_probs) < max_samples:
            for p in problems:
                if p not in sample_probs:
                    sample_probs.append(p)
                if len(sample_probs) == max_samples:
                    break
        eval_targets = sample_probs
    else:
        eval_targets = problems

    print(f"\n[Live Benchmark] Evaluating {len(eval_targets)} representative holdout problems with real LLM inference...")
    
    # 1. Deterministic Router Baseline
    baseline_router = DeterministicRouter()
    baseline_records = []
    
    print("--- Running Deterministic Baseline ---")
    for p in eval_targets:
        t0 = time.time()
        test_spec = p.get("test_code") or p.get("test") or ""
        state = baseline_router.run(p["requirement"], test_spec)
        dur = time.time() - t0
        passed = bool(state.test_result and state.test_result.passed)
        passed_t = state.test_result.passed_tests if state.test_result else 0
        total_t = state.test_result.total_tests if state.test_result else 0
        quality = state.review_feedback.quality_score if state.review_feedback else 0.0

        baseline_records.append({
            "id": p["id"],
            "difficulty": p.get("difficulty", "Medium"),
            "passed": passed,
            "steps": state.step_count,
            "time_seconds": dur,
            "passed_assertions": passed_t,
            "total_assertions": total_t,
            "quality_score": quality,
            "actions": list(state.action_history)
        })
        print(f"  [Baseline] {p['id']} ({p.get('difficulty')}): Passed={passed} ({passed_t}/{total_t}) in {state.step_count} steps ({dur:.2f}s)")

    # 2. RL Orchestrator
    rl_records = []
    model = PPO.load(model_path) if os.path.exists(model_path) else None
    env = MultiAgentCodingEnv(problems=eval_targets, max_steps=8, simulated=False)

    print("\n--- Running RL Orchestrator ---")
    for p in eval_targets:
        t0 = time.time()
        obs, info = env.reset(options={"problem": p})
        done = False
        step = 0
        total_rew = 0.0
        trajectory = []

        while not done and step < 8:
            action_mask = env.get_action_mask()
            if model:
                action, _ = model.predict(obs, deterministic=True)
                action = int(action)
                if not action_mask[action]:
                    action = int(np.where(action_mask)[0][0])
            else:
                action = int(np.where(action_mask)[0][0])

            trajectory.append(env.ACTION_MAP[action])
            obs, reward, terminated, truncated, info = env.step(action)
            total_rew += reward
            done = terminated or truncated
            step += 1

        dur = time.time() - t0
        s = env.current_state
        passed = bool(s.test_result and s.test_result.passed)
        passed_t = s.test_result.passed_tests if s.test_result else 0
        total_t = s.test_result.total_tests if s.test_result else 0
        quality = s.review_feedback.quality_score if s.review_feedback else 0.0

        rl_records.append({
            "id": p["id"],
            "difficulty": p.get("difficulty", "Medium"),
            "passed": passed,
            "steps": s.step_count,
            "time_seconds": dur,
            "reward": total_rew,
            "passed_assertions": passed_t,
            "total_assertions": total_t,
            "quality_score": quality,
            "trajectory": trajectory
        })
        print(f"  [RL Policy] {p['id']} ({p.get('difficulty')}): Passed={passed} ({passed_t}/{total_t}) in {s.step_count} steps ({dur:.2f}s) | Path: {' -> '.join(trajectory)}")

    # Aggregate summaries
    b_acc = (sum(1 for r in baseline_records if r["passed"]) / len(baseline_records)) * 100.0
    r_acc = (sum(1 for r in rl_records if r["passed"]) / len(rl_records)) * 100.0
    
    b_mean_steps = float(np.mean([r["steps"] for r in baseline_records]))
    r_mean_steps = float(np.mean([r["steps"] for r in rl_records]))

    b_mean_time = float(np.mean([r["time_seconds"] for r in baseline_records]))
    r_mean_time = float(np.mean([r["time_seconds"] for r in rl_records]))

    b_mean_quality = float(np.mean([r["quality_score"] for r in baseline_records]))
    r_mean_quality = float(np.mean([r["quality_score"] for r in rl_records]))

    b_total_pass_assertions = sum(r["passed_assertions"] for r in baseline_records)
    b_total_assertions = sum(r["total_assertions"] for r in baseline_records)
    r_total_pass_assertions = sum(r["passed_assertions"] for r in rl_records)
    r_total_assertions = sum(r["total_assertions"] for r in rl_records)

    step_reduction = ((b_mean_steps - r_mean_steps) / b_mean_steps) * 100.0 if b_mean_steps > 0 else 0.0
    time_reduction = ((b_mean_time - r_mean_time) / b_mean_time) * 100.0 if b_mean_time > 0 else 0.0

    return {
        "baseline": {
            "accuracy_pct": b_acc,
            "mean_steps": b_mean_steps,
            "mean_time_seconds": b_mean_time,
            "mean_quality_score": b_mean_quality,
            "assertions_passed": b_total_pass_assertions,
            "assertions_total": b_total_assertions,
            "assertion_pass_rate_pct": (b_total_pass_assertions / b_total_assertions * 100.0) if b_total_assertions else 0.0,
            "records": baseline_records
        },
        "rl_orchestrator": {
            "accuracy_pct": r_acc,
            "mean_steps": r_mean_steps,
            "mean_time_seconds": r_mean_time,
            "mean_quality_score": r_mean_quality,
            "assertions_passed": r_total_pass_assertions,
            "assertions_total": r_total_assertions,
            "assertion_pass_rate_pct": (r_total_pass_assertions / r_total_assertions * 100.0) if r_total_assertions else 0.0,
            "records": rl_records
        },
        "comparison": {
            "step_reduction_pct": step_reduction,
            "latency_reduction_pct": time_reduction,
            "speedup_factor": (b_mean_time / r_mean_time) if r_mean_time > 0 else 1.0
        }
    }

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    model_path = os.path.join(root, "training", "models", "ppo_orchestrator.zip")
    logs_dir = os.path.join(root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    print("=" * 70)
    print("      MULTI-AGENT CODING SYSTEM: COMPREHENSIVE PERFORMANCE METRICS     ")
    print("=" * 70)

    # 1. Dataset Breakdown
    dataset_metrics = calculate_dataset_metrics()
    print("\n1. BENCHMARK DATASET PROFILE:")
    print(f"   - Total Problems: {dataset_metrics['total_problems']}")
    print(f"   - Split Distribution: Train={dataset_metrics['train_count']} (70%), Val={dataset_metrics['val_count']} (15%), Test={dataset_metrics['test_count']} (15%)")
    print(f"   - Categories: {dict(dataset_metrics['full_stats']['categories'])}")
    print(f"   - Difficulties: {dict(dataset_metrics['full_stats']['difficulties'])}")

    # 2. Full Benchmark Simulated RL Orchestrator Evaluation (20 problems)
    full_problems = load_local_benchmark("all")
    simulated_metrics = evaluate_rl_simulated(full_problems, model_path)
    print("\n2. RL POLICY SIMULATION BENCHMARK (All 20 Problems):")
    print(f"   - Functional Accuracy (Pass Rate): {simulated_metrics['accuracy_pct']:.1f}% ({simulated_metrics['passed_count']}/{simulated_metrics['total_evaluated']})")
    print(f"   - Mean Agent Steps: {simulated_metrics['mean_steps']:.2f}")
    print(f"   - Mean Cumulative Reward: {simulated_metrics['mean_reward']:.2f}")

    # 3. Live Holdout Test Set Evaluation (3 problems: Easy, Medium, Hard)
    test_problems = load_local_benchmark("test")
    live_metrics = evaluate_live_comparison(test_problems, model_path)

    print("\n" + "=" * 70)
    print("3. LIVE LLM EVALUATION SUMMARY (Holdout Test Set):")
    print("=" * 70)
    b = live_metrics["baseline"]
    r = live_metrics["rl_orchestrator"]
    c = live_metrics["comparison"]

    print(f"{'Metric':<30} | {'Deterministic Baseline':<22} | {'RL Orchestrator':<18}")
    print("-" * 75)
    print(f"{'Task Pass Rate (Accuracy)':<30} | {b['accuracy_pct']:>20.1f}% | {r['accuracy_pct']:>16.1f}%")
    print(f"{'Assertion Pass Rate':<30} | {b['assertion_pass_rate_pct']:>20.1f}% | {r['assertion_pass_rate_pct']:>16.1f}%")
    print(f"{'Mean Agent Invocations':<30} | {b['mean_steps']:>20.2f}  | {r['mean_steps']:>16.2f} ")
    print(f"{'Mean Latency per Problem':<30} | {b['mean_time_seconds']:>19.2f}s | {r['mean_time_seconds']:>15.2f}s")
    print(f"{'Mean Code Review Score':<30} | {b['mean_quality_score']:>20.2f}  | {r['mean_quality_score']:>16.2f} ")
    print("-" * 75)
    print(f"Step Reduction:    {c['step_reduction_pct']:.1f}% fewer agent calls")
    print(f"Latency Reduction: {c['latency_reduction_pct']:.1f}% faster execution")
    print(f"Speedup Factor:    {c['speedup_factor']:.2f}x")
    print("=" * 70)

    # Export full metrics to JSON
    output_data = {
        "dataset_metrics": dataset_metrics,
        "simulated_rl_metrics": simulated_metrics,
        "live_metrics": live_metrics,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    json_path = os.path.join(logs_dir, "performance_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"\n[Saved] Detailed JSON metrics written to: {json_path}")

if __name__ == "__main__":
    main()
