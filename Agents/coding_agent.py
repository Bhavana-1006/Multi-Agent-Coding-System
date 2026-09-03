import re
from Agents.base_agent import BaseAgent
from schemas.state import ProjectState
from llm.client import generate

def extract_python_code(text: str) -> str:
    """Extracts Python code from markdown fences or returns clean text."""
    if not text:
        return ""
    # Find ```python ... ```
    match = re.search(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Otherwise strip leading/trailing fences
    clean = re.sub(r"^```(?:python)?\s*", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE).strip()
    return clean

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CodingAgent",
            description="Generates complete, bug-free source code based on requirements, plan, and retrieved context."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Synthesizing source code...")
        
        context_parts = [f"Problem Requirement:\n{state.raw_requirement}"]
        
        if state.structured_requirement:
            context_parts.append(
                f"Structured Spec:\nInputs: {state.structured_requirement.inputs}\n"
                f"Outputs: {state.structured_requirement.outputs}\n"
                f"Constraints: {state.structured_requirement.constraints}\n"
                f"Edge Cases: {state.structured_requirement.edge_cases}"
            )
            
        if state.plan:
            context_parts.append("Implementation Plan:\n" + "\n".join(state.plan))
            
        if state.retrieved_context:
            context_parts.append(f"Retrieved Patterns / Documentation:\n{state.retrieved_context}")
            
        full_context = "\n\n".join(context_parts)
        
        prompt = f"""Write complete, clean, production-quality Python code to solve the following problem:

{full_context}

IMPORTANT INSTRUCTIONS:
- Write ONLY executable Python code and required imports inside a ```python ... ``` block.
- Do NOT put usage examples in __main__; provide only the function/class definitions ready for unit testing.
"""
        response = generate(
            prompt=prompt,
            system_prompt="You are a Senior Principal Software Engineer writing robust, highly optimized, and bug-free code."
        )
        
        clean_code = extract_python_code(response)
        state.code = clean_code
        state.action_history.append(self.name)
        state.step_count += 1
        self.log(f"Generated {len(clean_code.splitlines())} lines of code.")
        return state
