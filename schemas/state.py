import numpy as np
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RequirementSpec(BaseModel):
    summary: str = ""
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    edge_cases: List[str] = Field(default_factory=list)
    target_language: str = "python"

class ReviewResult(BaseModel):
    quality_score: float = 0.0  # 0.0 to 1.0
    passed_review: bool = False
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class TestCaseDetail(BaseModel):
    name: str = ""
    assertion: str = ""
    passed: bool = False
    error: Optional[str] = None

class TestExecutionResult(BaseModel):
    __test__ = False  # Prevent pytest from treating this Pydantic class as a test suite
    passed: bool = False
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    test_details: List[TestCaseDetail] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    error_type: Optional[str] = None  # SyntaxError, AssertionError, TimeoutError, etc.

class ProjectState(BaseModel):
    raw_requirement: str
    structured_requirement: Optional[RequirementSpec] = None
    plan: Optional[List[str]] = None
    retrieved_context: Optional[str] = None
    code: Optional[str] = None
    review_feedback: Optional[ReviewResult] = None
    test_code: Optional[str] = None
    test_result: Optional[TestExecutionResult] = None
    error_analysis: Optional[str] = None
    difficulty: str = "Medium"
    repair_attempt_count: int = 0
    
    # Execution Tracking
    action_history: List[str] = Field(default_factory=list)
    step_count: int = 0
    max_steps: int = 10
    total_reward: float = 0.0
    is_terminal: bool = False
    
    def to_feature_vector(self) -> np.ndarray:
        """
        Converts the discrete/continuous project state into a fixed-size 15-dimensional
        feature vector for the RL observation space: Box(shape=(15,), low=0.0, high=1.0)
        """
        has_req = 1.0 if self.structured_requirement is not None else 0.0
        has_plan = 1.0 if (self.plan is not None and len(self.plan) > 0) else 0.0
        has_retrieval = 1.0 if (self.retrieved_context is not None and len(self.retrieved_context) > 0) else 0.0
        has_code = 1.0 if (self.code is not None and len(self.code.strip()) > 0) else 0.0
        
        has_review = 1.0 if self.review_feedback is not None else 0.0
        quality_score = float(self.review_feedback.quality_score) if self.review_feedback is not None else 0.0
        
        has_tests = 1.0 if (self.test_code is not None and len(self.test_code.strip()) > 0) else 0.0
        tests_passed = 1.0 if (self.test_result is not None and self.test_result.passed) else 0.0
        pass_ratio = 0.0
        if self.test_result is not None and self.test_result.total_tests > 0:
            pass_ratio = float(self.test_result.passed_tests) / float(self.test_result.total_tests)
            
        has_error_analysis = 1.0 if (self.error_analysis is not None and len(self.error_analysis.strip()) > 0) else 0.0
        step_progress = min(1.0, float(self.step_count) / float(max(1, self.max_steps)))
        recent_repair = 1.0 if (len(self.action_history) > 0 and self.action_history[-1] == "SelfRepairAgent") else 0.0

        # Extended features for RL simulation alignment:
        repair_count_norm = min(1.0, float(self.repair_attempt_count) / 3.0)
        has_syntax_error = 1.0 if (self.test_result is not None and self.test_result.error_type == "SyntaxError") else 0.0
        
        diff_lower = (self.difficulty or "medium").lower()
        if diff_lower == "easy":
            diff_norm = 0.0
        elif diff_lower == "hard":
            diff_norm = 1.0
        else:
            diff_norm = 0.5

        vec = np.array([
            has_req,            # 0: Structured requirements extracted
            has_plan,           # 1: Implementation plan available
            has_retrieval,      # 2: Knowledge retrieved
            has_code,           # 3: Code synthesized
            has_review,         # 4: Code reviewed
            quality_score,      # 5: Normalized quality score [0.0, 1.0]
            has_tests,          # 6: Tests generated/present
            tests_passed,       # 7: All tests passed (1.0) or not (0.0)
            pass_ratio,         # 8: Proportion of tests passed [0.0, 1.0]
            has_error_analysis, # 9: Error analysis performed
            step_progress,      # 10: Step count normalized [0.0, 1.0]
            recent_repair,      # 11: Most recent action was self-repair
            repair_count_norm,  # 12: Normalized repair attempt count [0.0, 1.0]
            has_syntax_error,   # 13: Binary flag for syntax errors [0.0, 1.0]
            diff_norm           # 14: Normalized problem difficulty [0.0, 0.5, 1.0]
        ], dtype=np.float32)
        
        return vec