import os
import sys
import json
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stable_baselines3 import PPO
from orchestrator.rl_orchestrator import MultiAgentCodingEnv
from orchestrator.deterministic_router import DeterministicRouter

def run_evaluation():
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_requirements.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        problems = json.load(f)
        
    print(f"Loaded {len(problems)} benchmark coding problems.")
    
    # 1. Evaluate Deterministic Baseline
    print("\n" + "="*50)
    print("Evaluating Baseline: Fixed Sequential Multi-Agent")
    print("="*50)
    router = DeterministicRouter()
    baseline_results = []
    
    for prob in problems:
        print(f"\n[Baseline] Problem: {prob['id']}")
        state = router.run(prob["requirement"], prob["test_code"])
        passed = bool(state.test_result and state.test_result.passed)
        baseline_results.append({
            "id": prob["id"],
            "passed": passed,
            "steps": state.step_count,
            "actions": state.action_history
        })
        print(f"Result: {'PASSED' if passed else 'FAILED'} in {state.step_count} steps.")
        
    # 2. Evaluate RL Orchestrator
    print("\n" + "="*50)
    print("Evaluating RL Orchestrator Policy")
    print("="*50)
    env = MultiAgentCodingEnv(problems=problems, max_steps=8)
    model_path = os.path.join(os.path.dirname(__file__), "models", "ppo_orchestrator.zip")
    
    rl_model = None
    if os.path.exists(model_path):
        print(f"Loading trained policy from {model_path}")
        try:
            rl_model = PPO.load(model_path)
        except Exception as e:
            print(f"Notice loading model: {e}")
            
    rl_results = []
    for prob in problems:
        obs, info = env.reset(options={"problem": prob})
        done = False
        step = 0
        total_rew = 0.0
        
        while not done and step < 8:
            action_mask = env.get_action_mask()
            if rl_model:
                action, _ = rl_model.predict(obs, deterministic=True)
                action = int(action)
                if not action_mask[action]:
                    if action_mask[0]: action = 0
                    elif action_mask[2]: action = 2
                    elif action_mask[4]: action = 4
                    elif action_mask[5]: action = 5
                    elif action_mask[6]: action = 6
                    elif action_mask[3]: action = 3
                    elif action_mask[7]: action = 7
                    else: action = 7
            else:
                if action_mask[0]: action = 0
                elif action_mask[2]: action = 2
                elif action_mask[4]: action = 4
                elif action_mask[5]: action = 5
                elif action_mask[6]: action = 6
                elif action_mask[3]: action = 3
                elif action_mask[7]: action = 7
                else: action = 7
                
            obs, reward, terminated, truncated, info = env.step(action)
            total_rew += reward
            done = terminated or truncated
            step += 1
            
        final_state = env.current_state
        passed = bool(final_state.test_result and final_state.test_result.passed)
        rl_results.append({
            "id": prob["id"],
            "passed": passed,
            "steps": final_state.step_count,
            "reward": total_rew,
            "actions": final_state.action_history
        })
        print(f"[RL Orchestrator] Problem {prob['id']}: {'PASSED' if passed else 'FAILED'} in {final_state.step_count} steps. Total Reward: {total_rew:.2f}")

    # 3. Print Comparison Table
    print("\n" + "="*60)
    print(f"{'Problem ID':<12} | {'Baseline Steps':<15} | {'RL Steps':<10} | {'Status':<10}")
    print("="*60)
    for b, r in zip(baseline_results, rl_results):
        status = "PASSED" if (b["passed"] and r["passed"]) else "PARTIAL"
        print(f"{b['id']:<12} | {b['steps']:<15} | {r['steps']:<10} | {status:<10}")
    print("="*60)

if __name__ == "__main__":
    run_evaluation()
