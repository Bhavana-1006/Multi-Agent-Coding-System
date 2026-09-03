from Agents.base_agent import BaseAgent
from schemas.state import ProjectState
from llm.client import generate

class ErrorAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ErrorAnalysisAgent",
            description="Analyzes test failures, tracebacks, and runtime exceptions to pinpoint root causes."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Analyzing test execution failure and tracebacks...")
        
        if not state.test_result or state.test_result.passed:
            state.error_analysis = "No errors detected; all tests are passing."
            state.action_history.append(self.name)
            state.step_count += 1
            return state
            
        err_context = f"Error Type: {state.test_result.error_type}\nStderr:\n{state.test_result.stderr}\nStdout:\n{state.test_result.stdout}"
        
        prompt = f"""You are debugging a failing Python code implementation. Analyze the error trace below and identify the exact root cause of the failure:

Requirements:
{state.raw_requirement}

Current Code:
```python
{state.code}
```

Test Code Executed:
```python
{state.test_code}
```

Test Failure Diagnostics:
{err_context}

Provide a concise breakdown:
1. Root Cause: What exact line or logic is causing the failure?
2. Expected vs Actual Behavior.
3. Recommended Fix: What specific code modification is required?
"""
        response = generate(
            prompt=prompt,
            system_prompt="You are a Master Debugger and Python Runtime Specialist."
        )
        
        state.error_analysis = response.strip()
        state.action_history.append(self.name)
        state.step_count += 1
        self.log("Identified root cause analysis for test failure.")
        return state
