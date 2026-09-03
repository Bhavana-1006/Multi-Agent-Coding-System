import os
import sys
import argparse
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from orchestrator.deterministic_router import DeterministicRouter
from orchestrator.rl_orchestrator import MultiAgentCodingEnv
from stable_baselines3 import PPO

console = Console()

def run_rl_pipeline(requirement: str, test_code: str = ""):
    console.print(Panel("[bold cyan]Starting AI Multi-Agent Coding Pipeline with RL Orchestrator[/bold cyan]"))
    
    env = MultiAgentCodingEnv(max_steps=8, simulated=False)
    obs, info = env.reset(options={"problem": {"requirement": requirement, "test_code": test_code}})
    
    model_path = "training/models/ppo_orchestrator.zip"
    model = None
    if os.path.exists(model_path):
        try:
            model = PPO.load(model_path)
            console.print(f"[green]Loaded trained PPO policy from {model_path}[/green]")
        except Exception as e:
            console.print(f"[yellow]Notice loading model: {e}. Using adaptive policy.[/yellow]")

    done = False
    step = 0
    
    while not done and step < 8:
        action_mask = env.get_action_mask()
        
        # Decide next action
        if model:
            action, _ = model.predict(obs, deterministic=True)
            action = int(action)
            
            # If predicted action is invalid/masked, fallback to highest priority valid action
            if not action_mask[action]:
                state = env.current_state
                if action_mask[0]: action = 0  # Plan
                elif action_mask[2]: action = 2  # Code
                elif action_mask[4]: action = 4  # Test
                elif action_mask[5]: action = 5  # Error Analysis
                elif action_mask[6]: action = 6  # Self-Repair
                elif action_mask[3]: action = 3  # Review
                elif action_mask[7]: action = 7  # Terminate
                else: action = int(np.where(action_mask)[0][0]) if np.any(action_mask) else 7
        else:
            state = env.current_state
            if action_mask[0]: action = 0
            elif action_mask[2]: action = 2
            elif action_mask[4]: action = 4
            elif action_mask[5]: action = 5
            elif action_mask[6]: action = 6
            elif action_mask[3]: action = 3
            elif action_mask[7]: action = 7
            else: action = 7

        action_name = env.ACTION_MAP.get(action, "Unknown")
        console.print(f"\n[bold magenta]Step {step+1}: RL Orchestrator selected -> {action_name}[/bold magenta]")
        
        obs, reward, terminated, truncated, info = env.step(action)
        console.print(f"[dim]Reward: {reward:+.2f} | Action History: {env.current_state.action_history}[/dim]")
        
        done = terminated or truncated
        step += 1

    final_state = env.current_state
    display_final_results(final_state)

def run_baseline_pipeline(requirement: str, test_code: str = ""):
    console.print(Panel("[bold yellow]Starting Baseline Fixed Sequential Multi-Agent Pipeline[/bold yellow]"))
    router = DeterministicRouter()
    state = router.run(requirement, test_code)
    display_final_results(state)

def display_final_results(state):
    console.print("\n" + "="*70)
    console.print("[bold green]Execution Complete - Final Solution Summary[/bold green]")
    console.print("="*70)
    
    # Table of Agent Sequence
    table = Table(title="Agent Execution Trace")
    table.add_column("Step", justify="center", style="cyan")
    table.add_column("Agent Invoked", style="magenta")
    for i, agent in enumerate(state.action_history, 1):
        table.add_row(str(i), agent)
    console.print(table)

    # Test Outcome
    if state.test_result:
        status_color = "bold green" if state.test_result.passed else "bold red"
        status_text = "ALL TESTS PASSED (VERIFIED)" if state.test_result.passed else f"TESTS FAILED ({state.test_result.error_type})"
        console.print(f"\nTest Status: [{status_color}]{status_text}[/{status_color}]")
        if state.test_result.stdout:
            console.print(f"[dim]Stdout: {state.test_result.stdout}[/dim]")
        if state.test_result.stderr:
            console.print(f"[red]Stderr: {state.test_result.stderr}[/red]")

    # Review Score
    if state.review_feedback:
        console.print(f"\nCode Quality Score: [bold cyan]{state.review_feedback.quality_score:.2f} / 1.0[/bold cyan]")
        if state.review_feedback.suggestions:
            console.print(f"Suggestions: {', '.join(state.review_feedback.suggestions)}")

    # Generated Code
    if state.code:
        console.print("\n[bold]Generated Source Code:[/bold]")
        syntax = Syntax(state.code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Coding System with RL Orchestration")
    parser.add_argument("--mode", choices=["rl", "baseline"], default="rl", help="Orchestration mode")
    parser.add_argument("--req", type=str, default="", help="Custom problem requirement")
    args = parser.parse_args()

    default_req = "Write a python function `is_palindrome(s: str) -> bool` that checks if a string is a palindrome, ignoring casing and non-alphanumeric characters."
    req = args.req if args.req else default_req
    
    if args.mode == "rl":
        run_rl_pipeline(req)
    else:
        run_baseline_pipeline(req)

if __name__ == "__main__":
    main()