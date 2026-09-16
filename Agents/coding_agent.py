import re
import ast
from concurrent.futures import ThreadPoolExecutor
from Agents.base_agent import BaseAgent
from schemas.state import ProjectState
from execution.pytest_runner import run_tests_in_sandbox
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
    def __init__(self, n_candidates: int = 3):
        super().__init__(
            name="CodingAgent",
            description="Generates complete, bug-free source code based on requirements, plan, and retrieved context."
        )
        self.n_candidates = n_candidates

    def _generate_single_candidate(self, prompt: str, temperature: float = 0.2) -> str:
        response = generate(
            prompt=prompt,
            system_prompt="You are a Senior Principal Software Engineer writing robust, highly optimized, and bug-free code.",
            temperature=temperature,
            max_tokens=4096
        )
        return extract_python_code(response)

    def run(self, state: ProjectState) -> ProjectState:
        self.log(f"Synthesizing source code (Best-of-{self.n_candidates} sampling)...")
        
        context_parts = [f"Problem Requirement:\n{state.raw_requirement}"]
        
        if state.structured_requirement:
            spec = state.structured_requirement
            context_parts.append(
                f"Structured Spec:\n"
                f"- Inputs: {', '.join(spec.inputs) if spec.inputs else 'N/A'}\n"
                f"- Outputs: {', '.join(spec.outputs) if spec.outputs else 'N/A'}\n"
                f"- Constraints: {', '.join(spec.constraints) if spec.constraints else 'N/A'}\n"
                f"- Edge Cases: {', '.join(spec.edge_cases) if spec.edge_cases else 'N/A'}"
            )
            
        if state.plan:
            context_parts.append("Implementation Plan:\n" + "\n".join(state.plan))
            
        if state.retrieved_context:
            context_parts.append(f"Retrieved Patterns / Documentation:\n{state.retrieved_context}")
            
        full_context = "\n\n".join(context_parts)
        
        prompt = f"""Write complete, clean, production-quality Python code to solve the following problem:

{full_context}

IMPORTANT INSTRUCTIONS:
- Function Names: Maintain exact function and class names specified in the requirement.
- Imports: Include all necessary standard library imports (e.g. typing, collections, math, functools).
- Edge Cases: Explicitly guard against empty inputs, boundaries, and negative or out-of-bound conditions.
- Format: Write ONLY executable Python code inside a ```python ... ``` block.
- Do NOT include interactive `input()`, example runs, or `if __name__ == '__main__':` blocks.
"""
        candidates = []
        if self.n_candidates <= 1:
            candidates.append(self._generate_single_candidate(prompt, temperature=0.1))
        else:
            temperatures = [0.1, 0.3, 0.4][:self.n_candidates]
            with ThreadPoolExecutor(max_workers=self.n_candidates) as executor:
                futures = [executor.submit(self._generate_single_candidate, prompt, temp) for temp in temperatures]
                for f in futures:
                    cand = f.result()
                    if cand and cand.strip():
                        candidates.append(cand)
                        
        if not candidates:
            candidates = [self._generate_single_candidate(prompt, temperature=0.1)]

        best_code = candidates[0]
        best_score = -1.0
        
        for idx, cand in enumerate(candidates):
            try:
                compile(cand, "<string>", "exec")
                syntax_valid = True
            except SyntaxError:
                syntax_valid = False
                
            if not syntax_valid:
                continue

            if state.test_code and state.test_code.strip():
                res = run_tests_in_sandbox(code=cand, test_code=state.test_code, timeout=4.0)
                if res.passed:
                    self.log(f"Candidate #{idx+1} PASSED all unit tests! Selected.")
                    best_code = cand
                    state.test_result = res
                    break
                else:
                    ratio = (res.passed_tests / max(1, res.total_tests)) if res.total_tests > 0 else 0.0
                    if ratio > best_score:
                        best_score = ratio
                        best_code = cand
            else:
                best_code = cand
                break
                
        state.code = best_code
        state.action_history.append(self.name)
        state.step_count += 1
        self.log(f"Selected code implementation ({len(best_code.splitlines())} lines).")
        return state
