from Agents.base_agent import BaseAgent
from schemas.state import ProjectState, RequirementSpec
from llm.client import generate_json

class RequirementAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RequirementAnalyzer",
            description="Analyzes, structures, and extracts inputs, outputs, constraints, and edge cases."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Analyzing and structuring user requirement...")
        
        prompt = f"""Analyze the following software requirement and extract structured technical specifications:
Requirement:
\"\"\"
{state.raw_requirement}
\"\"\"

Extract:
1. summary: A 1-2 sentence technical summary
2. inputs: List of expected input arguments, types, and descriptions
3. outputs: List of expected return types and values
4. constraints: List of algorithmic/complexity or environment constraints
5. edge_cases: List of critical boundary conditions (e.g. empty lists, negative numbers, large inputs)
6. target_language: Target programming language (e.g., 'python')
"""
        spec = generate_json(
            prompt=prompt,
            schema_class=RequirementSpec,
            system_prompt="You are an expert Software Architect and Requirements Engineer."
        )
        
        state.structured_requirement = spec
        state.action_history.append(self.name)
        state.step_count += 1
        self.log(f"Extracted {len(spec.inputs)} inputs, {len(spec.constraints)} constraints, and {len(spec.edge_cases)} edge cases.")
        return state
