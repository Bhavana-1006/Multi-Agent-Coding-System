import ast
import re
from Agents.base_agent import BaseAgent
from schemas.state import ProjectState, TestExecutionResult
from execution.pytest_runner import run_tests_in_sandbox
from llm.client import generate

def extract_python_code(text: str) -> str:
    if not text: return ""
    match = re.search(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)
    if match: return match.group(1).strip()
    clean = re.sub(r"^```(?:python)?\s*", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE).strip()
    return clean

def extract_interface_signatures(code: str) -> list[str]:
    """Extracts top-level function and class signatures without implementation bodies."""
    if not code:
        return []
    signatures = []
    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                signatures.append(f"def {node.name}({', '.join(args)}): ...")
            elif isinstance(node, ast.ClassDef):
                signatures.append(f"class {node.name}: ...")
    except Exception:
        matches = re.findall(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\(.*?\)):", code)
        signatures = [f"def {m}: ..." for m in matches]
    return signatures

class TestingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TestingAgent",
            description="Generates unit tests (if not already present) and executes tests in the sandbox."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Running automated testing suite in sandbox...")
        
        if not state.code or not state.code.strip():
            state.test_result = TestExecutionResult(
                passed=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                stdout="",
                stderr="No code available to test.",
                error_type="MissingCode"
            )
            state.action_history.append(self.name)
            state.step_count += 1
            return state
            
        # If test_code has not been defined yet, generate unit tests (Contract-First)
        if not state.test_code or not state.test_code.strip():
            self.log("Generating contract-first unit test cases from specifications...")
            
            context_parts = [f"Problem Requirement:\n{state.raw_requirement}"]
            
            if state.structured_requirement:
                spec = state.structured_requirement
                context_parts.append(
                    f"Specification Contract:\n"
                    f"- Summary: {spec.summary}\n"
                    f"- Expected Inputs: {', '.join(spec.inputs) if spec.inputs else 'N/A'}\n"
                    f"- Expected Outputs: {', '.join(spec.outputs) if spec.outputs else 'N/A'}\n"
                    f"- Constraints: {', '.join(spec.constraints) if spec.constraints else 'N/A'}\n"
                    f"- Critical Edge Cases: {', '.join(spec.edge_cases) if spec.edge_cases else 'N/A'}"
                )
                
            signatures = extract_interface_signatures(state.code)
            if signatures:
                context_parts.append("Target Callable Signatures to test:\n" + "\n".join(signatures))
                
            full_context = "\n\n".join(context_parts)
            
            prompt = f"""You are a Lead QA Engineer writing exhaustive, black-box unit tests based STRICTLY on requirements and contracts.

{full_context}

REQUIREMENTS FOR TEST SUITE:
1. Ground Truth Verification: Calculate expected results mathematically and logically from the requirements. Do NOT guess.
2. Coverage: Include 5-8 diverse test cases:
   - Standard typical use cases.
   - Boundary conditions and extreme limits.
   - All critical edge cases listed above (e.g. empty inputs, negative values, single elements, type edge cases).
3. Format: Return ONLY executable Python assertions inside a ```python ... ``` block.
   Example:
   assert target_function(arg1, arg2) == expected_result
   assert target_function(edge_case_input) == expected_edge_result
4. Do NOT import unittest or write dummy assertions like `assert True`. Write concrete, validating assertions.
"""
            test_response = generate(
                prompt=prompt,
                system_prompt="You are a Principal Software Quality Assurance Engineer specializing in contract-first black-box testing.",
                temperature=0.2,
                max_tokens=2048
            )
            
            clean_tests = extract_python_code(test_response)
            state.test_code = clean_tests
            
        # Execute tests in sandbox
        result = run_tests_in_sandbox(code=state.code, test_code=state.test_code, timeout=5.0)
        state.test_result = result
        state.action_history.append(self.name)
        state.step_count += 1
        
        if result.passed:
            self.log(f"All {result.total_tests} tests PASSED! Verified.")
        else:
            self.log(f"Tests FAILED ({result.failed_tests}/{result.total_tests} failed). Error: {result.error_type}")
            
        return state
