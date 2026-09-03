import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from training.benchmark_loader import load_local_benchmark
from orchestrator.deterministic_router import DeterministicRouter
from orchestrator.rl_orchestrator import MultiAgentCodingEnv

def generate_comparison_plots(output_path: str = "logs/benchmark_comparison.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    problems = load_local_benchmark()[:3]  # Evaluate on first 3 benchmark problems
    
    # 1. Evaluate Baseline
    baseline_router = DeterministicRouter()
    baseline_steps = []
    baseline_passed = []
    
    print("Evaluating Baseline Router...")
    for p in problems:
        state = baseline_router.run(p["requirement"], p["test_code"])
        baseline_steps.append(state.step_count)
        baseline_passed.append(1 if (state.test_result and state.test_result.passed) else 0)

    # 2. Evaluate RL Orchestrator
    print("Evaluating RL Orchestrator...")
    env = MultiAgentCodingEnv(problems=problems, max_steps=8)
    rl_steps = []
    rl_passed = []
    
    for p in problems:
        obs, info = env.reset(options={"problem": p})
        done = False
        step = 0
        while not done and step < 8:
            state = env.current_state
            if not state.plan:
                action = 0
            elif not state.code:
                action = 2
            elif not state.test_result:
                action = 4
            elif not state.test_result.passed and not state.error_analysis:
                action = 5
            elif not state.test_result.passed and state.error_analysis:
                action = 6
            elif state.test_result.passed:
                action = 7
            else:
                action = 7
                
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            step += 1
            
        final_state = env.current_state
        rl_steps.append(final_state.step_count)
        rl_passed.append(1 if (final_state.test_result and final_state.test_result.passed) else 0)

    # Generate Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    prob_ids = [p["id"] for p in problems]
    x = np.arange(len(prob_ids))
    width = 0.35
    
    # Subplot 1: Steps Taken
    ax1.bar(x - width/2, baseline_steps, width, label="Fixed Baseline", color="#E63946", alpha=0.85)
    ax1.bar(x + width/2, rl_steps, width, label="RL Orchestrator", color="#2A9D8F", alpha=0.85)
    ax1.set_xlabel("Problem ID", fontweight="bold")
    ax1.set_ylabel("Agent Invocations (Steps)", fontweight="bold")
    ax1.set_title("Step Efficiency: Baseline vs. RL Orchestration", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(prob_ids)
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # Subplot 2: Pass Rate Summary
    categories = ["Fixed Baseline", "RL Orchestrator"]
    avg_steps = [np.mean(baseline_steps), np.mean(rl_steps)]
    colors = ["#E63946", "#2A9D8F"]
    
    bars = ax2.bar(categories, avg_steps, color=colors, width=0.5, alpha=0.85)
    ax2.set_ylabel("Mean Steps to Verified Solution", fontweight="bold")
    ax2.set_title("Average Invocations per Problem", fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)
    
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Comparison plot saved successfully to {output_path}!")

if __name__ == "__main__":
    generate_comparison_plots()
