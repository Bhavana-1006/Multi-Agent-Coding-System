from Agents.base_agent import BaseAgent
from schemas.state import ProjectState, ReviewResult
from llm.client import generate_json

class ReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ReviewAgent",
            description="Reviews generated code for syntax, style, algorithmic efficiency, and edge case coverage."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Reviewing generated code for quality and standards...")
        
        if not state.code or not state.code.strip():
            state.review_feedback = ReviewResult(
                quality_score=0.0,
                passed_review=False,
                issues=["No code available to review."],
                suggestions=["Invoke CodingAgent first to generate code."]
            )
            state.action_history.append(self.name)
            state.step_count += 1
            return state
            
        prompt = f"""Review the following Python code against the requirements:

Requirements:
{state.raw_requirement}

Code to Review:
```python
{state.code}
```

Evaluate:
1. quality_score: A float from 0.0 to 1.0 (1.0 = flawless, efficient, handles all edge cases; <0.6 = has bugs or missing handling).
2. passed_review: True if score >= 0.8 and no critical bugs found, False otherwise.
3. issues: List of potential bugs, syntax defects, or unhandled edge cases.
4. suggestions: List of concrete code improvement suggestions.
"""
        review = generate_json(
            prompt=prompt,
            schema_class=ReviewResult,
            system_prompt="You are a strict Senior Staff Code Reviewer and QA Engineer."
        )
        
        state.review_feedback = review
        state.action_history.append(self.name)
        state.step_count += 1
        self.log(f"Review completed. Quality Score: {review.quality_score:.2f}, Passed: {review.passed_review}")
        return state
