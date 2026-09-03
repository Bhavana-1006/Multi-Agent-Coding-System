import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Dict, Any, Tuple, List

from schemas.state import ProjectState, RequirementSpec, ReviewResult, TestExecutionResult
from Agents.requirement_analyzer import RequirementAnalyzerAgent
from Agents.planning_agent import PlanningAgent
from Agents.retrieval_agent import RetrievalAgent
from Agents.coding_agent import CodingAgent
from Agents.review_agent import ReviewAgent
from Agents.testing_agent import TestingAgent
from Agents.error_analysis_agent import ErrorAnalysisAgent
from Agents.self_repair_agent import SelfRepairAgent

class MultiAgentCodingEnv(gym.Env):
    """
    Gymnasium Environment for RL Orchestration of Multi-Agent Software Development.
    Supports live LLM agent execution, strict action masking, and fast simulated training mode.
    """
    metadata = {"render_modes": ["human"]}

    ACTION_MAP = {
        0: "PlanningAgent",
        1: "RetrievalAgent",
        2: "CodingAgent",
        3: "ReviewAgent",
        4: "TestingAgent",
        5: "ErrorAnalysisAgent",
        6: "SelfRepairAgent",
        7: "Terminate"
    }

    def __init__(
        self,
        problems: Optional[List[Dict[str, str]]] = None,
        max_steps: int = 8,
        simulated: bool = False
    ):
        super().__init__()
        
        self.max_steps = max_steps
        self.simulated = simulated
        self.problems = problems or [
            {
                "id": "prob_001",
                "requirement": "Write a python function `is_palindrome(s: str) -> bool` that returns True if a given string is a palindrome, ignoring casing and non-alphanumeric characters, and False otherwise.",
                "test_code": "assert is_palindrome('A man, a plan, a canal: Panama') == True\nassert is_palindrome('race a car') == False\nassert is_palindrome('') == True\nassert is_palindrome('0P') == False"
            },
            {
                "id": "prob_002",
                "requirement": "Write a python function `two_sum(nums: list[int], target: int) -> list[int]` that returns the indices of the two numbers such that they add up to target. Assume exactly one solution exists.",
                "test_code": "assert two_sum([2, 7, 11, 15], 9) == [0, 1]\nassert two_sum([3, 2, 4], 6) == [1, 2]\nassert two_sum([3, 3], 6) == [0, 1]"
            },
            {
                "id": "prob_003",
                "requirement": "Write a python function `fibonacci(n: int) -> int` that returns the n-th Fibonacci number where fibonacci(0) = 0 and fibonacci(1) = 1.",
                "test_code": "assert fibonacci(0) == 0\nassert fibonacci(1) == 1\nassert fibonacci(5) == 5\nassert fibonacci(10) == 55"
            }
        ]
        
        # 12-dimensional observation vector describing project state
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(12,),
            dtype=np.float32
        )
        
        # 8 discrete actions (7 agents + 1 termination action)
        self.action_space = spaces.Discrete(8)
        
        # Initialize live agents
        self.req_analyzer = RequirementAnalyzerAgent()
        self.agents = {
            0: PlanningAgent(),
            1: RetrievalAgent(),
            2: CodingAgent(),
            3: ReviewAgent(),
            4: TestingAgent(),
            5: ErrorAnalysisAgent(),
            6: SelfRepairAgent(),
        }
        
        self.current_state: Optional[ProjectState] = None
        self.current_problem_idx: int = 0

    def get_action_mask(self) -> np.ndarray:
        """
        Computes strict validity mask for the 8 actions given the current state.
        [Plan, Retrieve, Code, Review, Test, AnalyzeError, Repair, Terminate]
        """
        mask = np.zeros(8, dtype=bool)
        if self.current_state is None:
            mask[:] = True
            return mask
            
        s = self.current_state
        has_code = bool(s.code and s.code.strip())
        has_plan = bool(s.plan and len(s.plan) > 0)
        has_retrieval = bool(s.retrieved_context)
        has_review = bool(s.review_feedback is not None)
        tests_passed = bool(s.test_result and s.test_result.passed)
        tests_failed = bool(s.test_result and not s.test_result.passed and s.test_result.total_tests > 0)
        has_error_diag = bool(s.error_analysis and len(s.error_analysis.strip()) > 0)

        if tests_passed:
            # Code is already verified! Only review (optional) or terminate are valid.
            if not has_review:
                mask[3] = True  # Review
            mask[7] = True  # Terminate
            return mask

        if tests_failed:
            # Tests failed. Re-testing the exact same failing code is FORBIDDEN.
            # Must perform Error Analysis -> Self Repair.
            if not has_error_diag:
                mask[5] = True  # Error Analysis
            else:
                mask[6] = True  # Self Repair
            return mask

        # Initial / developing stage (tests not passed yet):
        if not has_plan:
            mask[0] = True  # Plan
        if not has_retrieval:
            mask[1] = True  # Retrieve
        if not has_code:
            mask[2] = True  # Code
        else:
            # Has code, but untested
            mask[4] = True  # Test
            if not has_review:
                mask[3] = True  # Review

        if not np.any(mask):
            mask[4] = True
            mask[7] = True
            
        return mask

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        
        if options and "problem" in options:
            prob = options["problem"]
        else:
            if seed is not None:
                np.random.seed(seed)
            self.current_problem_idx = np.random.randint(0, len(self.problems))
            prob = self.problems[self.current_problem_idx]
            
        self.current_state = ProjectState(
            raw_requirement=prob["requirement"],
            test_code=prob.get("test_code", ""),
            max_steps=self.max_steps
        )
        
        if self.simulated:
            self.current_state.structured_requirement = RequirementSpec(
                summary="Simulated problem requirement",
                inputs=["arg1"],
                outputs=["res"]
            )
            self.current_state.action_history.append("RequirementAnalyzer")
            self.current_state.step_count = 1
        else:
            self.current_state = self.req_analyzer.run(self.current_state)
            
        obs = self.current_state.to_feature_vector()
        info = {
            "requirement": self.current_state.raw_requirement,
            "step_count": self.current_state.step_count,
            "action_mask": self.get_action_mask()
        }
        return obs, info

    def _simulated_step(self, action: int) -> ProjectState:
        s = self.current_state
        action_name = self.ACTION_MAP[action]
        s.action_history.append(action_name)
        s.step_count += 1
        
        if action == 0:  # Planning
            s.plan = ["Step 1: Parse input", "Step 2: Compute solution", "Step 3: Return result"]
        elif action == 1:  # Retrieval
            s.retrieved_context = "Relevant library algorithm documentation snippet."
        elif action == 2:  # Coding
            s.code = "def solution(): return True"
            s.test_result = None
        elif action == 3:  # Review
            s.review_feedback = ReviewResult(quality_score=0.95, passed_review=True)
        elif action == 4:  # Testing
            if s.code:
                s.test_result = TestExecutionResult(passed=True, total_tests=5, passed_tests=5, failed_tests=0)
            else:
                s.test_result = TestExecutionResult(passed=False, total_tests=1, failed_tests=1, error_type="MissingCode")
        elif action == 5:  # Error Analysis
            s.error_analysis = "Diagnosed root cause: variable edge case mismatch."
        elif action == 6:  # Self Repair
            s.code = "def solution_repaired(): return True"
            s.test_result = None
            s.error_analysis = None
            
        return s

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self.current_state is None:
            raise RuntimeError("Environment must be reset before stepping.")
            
        action_name = self.ACTION_MAP.get(action, "Unknown")
        reward = -0.1  # Minimal step penalty for finding short paths
        terminated = False
        truncated = False
        
        s = self.current_state
        has_code = bool(s.code and s.code.strip())
        has_plan = bool(s.plan and len(s.plan) > 0)
        has_retrieval = bool(s.retrieved_context)
        tests_passed = bool(s.test_result and s.test_result.passed)
        tests_failed = bool(s.test_result and not s.test_result.passed and s.test_result.total_tests > 0)
        
        # Action 7: Terminate / Submit Solution
        if action == 7:
            s.action_history.append("Terminate")
            s.step_count += 1
            terminated = True
            
            if tests_passed:
                reward += 10.0  # Big reward for verified passing solution
                if s.review_feedback:
                    reward += 2.0 * s.review_feedback.quality_score
            else:
                reward -= 10.0  # Heavy penalty for submitting without verified passing tests
                
            obs = s.to_feature_vector()
            info = {
                "action": action_name,
                "passed": tests_passed,
                "history": s.action_history,
                "action_mask": self.get_action_mask()
            }
            return obs, reward, terminated, truncated, info

        # Repetition and Illegal Action Penalties
        if action == 0:  # Planning
            if has_plan: reward -= 5.0
            else: reward += 1.5
        elif action == 1:  # Retrieval
            if has_retrieval: reward -= 5.0
            else: reward += 0.8
        elif action == 2:  # Coding
            if tests_passed: reward -= 5.0
            elif has_code and not tests_failed: reward -= 3.0
            else: reward += 2.0
        elif action == 3:  # Review
            if not has_code: reward -= 5.0
            elif s.review_feedback is not None: reward -= 3.0
            else: reward += 1.0
        elif action == 4:  # Testing
            if not has_code: reward -= 5.0
            elif tests_passed: reward -= 3.0
            elif tests_failed: reward -= 5.0  # Cannot re-test failed code without repair
            else: reward += 2.0
        elif action == 5:  # Error Analysis
            if not tests_failed: reward -= 5.0
            else: reward += 2.0
        elif action == 6:  # Self Repair
            if not tests_failed: reward -= 5.0
            else: reward += 2.5

        # Execute agent (Simulated or Live)
        if self.simulated:
            self.current_state = self._simulated_step(action)
        else:
            agent = self.agents[action]
            self.current_state = agent.run(self.current_state)
            
        # Post-action test execution reward adjustments
        if action == 4:
            if self.current_state.test_result and self.current_state.test_result.passed:
                reward += 4.0
            elif self.current_state.test_result and not self.current_state.test_result.passed:
                reward -= 1.0

        # Check step count timeout
        if self.current_state.step_count >= self.max_steps:
            truncated = True
            reward -= 5.0

        self.current_state.total_reward += reward
        obs = self.current_state.to_feature_vector()
        info = {
            "action": action_name,
            "passed": bool(self.current_state.test_result.passed) if self.current_state.test_result else False,
            "step": self.current_state.step_count,
            "history": self.current_state.action_history,
            "action_mask": self.get_action_mask()
        }
        
        return obs, reward, terminated, truncated, info

    def render(self):
        if self.current_state:
            print(f"[State Step: {self.current_state.step_count}] History: {self.current_state.action_history}")
