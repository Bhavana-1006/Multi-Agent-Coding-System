import os
import sys
import json
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gymnasium as gym
from stable_baselines3 import PPO
from orchestrator.rl_orchestrator import MultiAgentCodingEnv

def train(total_timesteps: int = 3000, save_dir: str = "training/models", simulated: bool = True):
    os.makedirs(save_dir, exist_ok=True)
    
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_requirements.json")
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            problems = json.load(f)
    else:
        problems = None

    print(f"Initializing MultiAgentCodingEnv (simulated={simulated}) with {len(problems) if problems else 3} problems...")
    env = MultiAgentCodingEnv(problems=problems, max_steps=8, simulated=simulated)
    
    print("Setting up PPO Policy Network (Actor-Critic MLP)...")
    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=0.001,
        n_steps=64,
        batch_size=32,
        n_epochs=10,
        gamma=0.99,
        ent_coef=0.01,
        verbose=1,
    )
    
    print(f"Training PPO Orchestrator for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)
    
    model_path = os.path.join(save_dir, "ppo_orchestrator.zip")
    model.save(model_path)
    print(f"\n[Success] Trained PPO Policy saved to: {model_path}")
    
    return model, env

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train PPO RL Orchestrator")
    parser.add_argument("--timesteps", type=int, default=3000, help="Total environment steps for training")
    parser.add_argument("--save_dir", type=str, default="training/models", help="Save directory")
    parser.add_argument("--live", action="store_true", help="Train with live LLM calls instead of simulated environment")
    args = parser.parse_args()
    
    train(total_timesteps=args.timesteps, save_dir=args.save_dir, simulated=not args.live)
