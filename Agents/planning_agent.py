import json
import re
from typing import List
from Agents.base_agent import BaseAgent
from schemas.state import ProjectState
from llm.client import generate

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PlanningAgent",
            description="Decomposes tasks and creates a step-by-step implementation plan."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Creating implementation plan and subtasks...")
        
        req_context = state.raw_requirement
        if state.structured_requirement:
            req_context += f"\nSummary: {state.structured_requirement.summary}"
            req_context += f"\nInputs: {state.structured_requirement.inputs}"
            req_context += f"\nOutputs: {state.structured_requirement.outputs}"
            req_context += f"\nConstraints: {state.structured_requirement.constraints}"
            req_context += f"\nEdge Cases: {state.structured_requirement.edge_cases}"
            
        prompt = f"""Based on the following software requirements, generate a concise, ordered list of development steps to implement the solution cleanly and handle all edge cases:

Requirements:
{req_context}

Output format: Return ONLY a numbered list of concrete steps (e.g. 1. Define signature..., 2. Handle base cases...).
"""
        response = generate(
            prompt=prompt,
            system_prompt="You are a Lead Software Architect specializing in clean code and algorithmic planning."
        )
        
        steps = [line.strip() for line in response.split("\n") if line.strip() and re.match(r"^\d+[\.\)]", line.strip())]
        if not steps:
            steps = [s.strip() for s in response.split("\n") if s.strip()]
            
        state.plan = steps
        state.action_history.append(self.name)
        state.step_count += 1
        self.log(f"Generated plan with {len(steps)} steps.")
        return state
