from schemas.state import ProjectState
from Agents.requirement_analyzer import RequirementAnalyzerAgent
from Agents.planning_agent import PlanningAgent
from Agents.retrieval_agent import RetrievalAgent
from Agents.coding_agent import CodingAgent
from Agents.review_agent import ReviewAgent
from Agents.testing_agent import TestingAgent
from Agents.error_analysis_agent import ErrorAnalysisAgent
from Agents.self_repair_agent import SelfRepairAgent

class DeterministicRouter:
    """
    Standard sequential multi-agent baseline (fixed execution pipeline).
    Used as the comparison benchmark against the RL Orchestrator.
    """
    def __init__(self, max_repair_attempts: int = 2):
        self.req_analyzer = RequirementAnalyzerAgent()
        self.planner = PlanningAgent()
        self.retriever = RetrievalAgent()
        self.coder = CodingAgent()
        self.reviewer = ReviewAgent()
        self.tester = TestingAgent()
        self.error_analyzer = ErrorAnalysisAgent()
        self.repairer = SelfRepairAgent()
        self.max_repair_attempts = max_repair_attempts

    def run(self, requirement: str, test_code: str = "") -> ProjectState:
        state = ProjectState(raw_requirement=requirement, test_code=test_code)
        
        # 1. Structure requirements
        state = self.req_analyzer.run(state)
        
        # 2. Plan
        state = self.planner.run(state)
        
        # 3. Retrieve
        state = self.retriever.run(state)
        
        # 4. Code
        state = self.coder.run(state)
        
        # 5. Review
        state = self.reviewer.run(state)
        
        # 6. Test
        state = self.tester.run(state)
        
        # 7. Error Analysis & Self-Repair loop if tests fail
        attempts = 0
        while state.test_result and not state.test_result.passed and attempts < self.max_repair_attempts:
            attempts += 1
            state = self.error_analyzer.run(state)
            state = self.repairer.run(state)
            state = self.tester.run(state)
            
        return state
