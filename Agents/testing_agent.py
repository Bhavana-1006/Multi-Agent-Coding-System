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
            
        # If test_code has not been defined yet, generate unit tests
        if not state.test_code or not state.test_code.strip():
            self.log("Generating automated unit test cases...")
            prompt = f"""Generate exhaustive Python unit test assertions (or pytest test functions) for the following code and requirements:

Requirement:
{state.raw_requirement}

Implementation Code:
```python
{state.code}
```

Requirements for tests:
- Include at least 4-6 test cases including typical cases and boundary conditions.
- Write pure Python test assertions inside a ```python ... ``` block like:
assert func(...) == expected
"""
            test_response = generate(
                prompt=prompt,
                system_prompt="You are a Lead QA Engineer writing exhaustive unit tests."
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
