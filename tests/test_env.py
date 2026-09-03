import pytest
import numpy as np
from schemas.state import ProjectState, RequirementSpec, ReviewResult, TestExecutionResult

def test_state_vectorization():
    state = ProjectState(
        raw_requirement="Implement binary search",
        structured_requirement=RequirementSpec(summary="Binary search", inputs=["arr", "target"], outputs=["int"]),
        plan=["Step 1: left=0, right=len(arr)-1", "Step 2: binary search loop"],
        retrieved_context="Binary search template",
        code="def binary_search(arr, target): return 0",
        review_feedback=ReviewResult(quality_score=0.9, passed_review=True),
        test_code="assert binary_search([1, 2, 3], 2) == 1",
        test_result=TestExecutionResult(passed=True, total_tests=1, passed_tests=1, failed_tests=0),
        step_count=3,
        max_steps=10
    )
    
    vec = state.to_feature_vector()
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (12,)
    assert vec[0] == 1.0  # has_req
    assert vec[1] == 1.0  # has_plan
    assert vec[3] == 1.0  # has_code
    assert vec[5] == 0.9  # quality score
    assert vec[7] == 1.0  # tests_passed
    assert np.all(vec >= 0.0) and np.all(vec <= 1.0)
