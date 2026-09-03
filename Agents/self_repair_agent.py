import re
from Agents.base_agent import BaseAgent
from schemas.state import ProjectState
from llm.client import generate

class SelfRepairAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SelfRepairAgent",
            description="Fixes bugs and refines code based on test feedback and root-cause analysis."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Applying self-repair to fix detected defects...")
        
        if not state.code or not state.code.strip():
            state.action_history.append(self.name)
            state.step_count += 1
            return state
            
        repair_context = []
        if state.error_analysis:
            repair_context.append(f"Root Cause Diagnostics:\n{state.error_analysis}")
            
        if state.test_result and not state.test_result.passed:
            repair_context.append(f"Test Stderr:\n{state.test_result.stderr}")
            
        if state.review_feedback and not state.review_feedback.passed_review:
            repair_context.append(f"Review Issues:\n{state.review_feedback.issues}")
            
        full_diag = "\n\n".join(repair_context) if repair_context else "Refactor and optimize the implementation."
        
        prompt = f"""You are a Python Self-Repair Agent. Fix all bugs and modify the code so it satisfies all requirements and passes all tests:

Requirements:
{state.raw_requirement}

Current Buggy Code:
```python
{state.code}
```

Diagnostics & Feedback:
{full_diag}

INSTRUCTIONS:
- Return ONLY the updated, fully repaired Python code.
- Do NOT include markdown commentary or conversation.
- Ensure the fix handles all edge cases.
"""
        response = generate(
            prompt=prompt,
            system_prompt="You are an Autonomous Self-Repair Coding Specialist."
        )
        
        clean_code = re.sub(r"^```(?:python)?\s*", "", response.strip(), flags=re.MULTILINE)
        clean_code = re.sub(r"```$", "", clean_code.strip(), flags=re.MULTILINE).strip()
        
        state.code = clean_code
        # Reset test_result since code has been modified and must be re-tested
        state.test_result = None
        state.action_history.append(self.name)
        state.step_count += 1
        self.log(f"Self-repair patch generated ({len(clean_code.splitlines())} lines). Ready for testing.")
        return state
