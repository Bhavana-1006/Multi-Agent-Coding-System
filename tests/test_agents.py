import pytest
from schemas.state import ProjectState, TestExecutionResult
from Agents.retrieval_agent import RetrievalAgent

def test_retrieval_agent():
    agent = RetrievalAgent()
    state = ProjectState(raw_requirement="Find palindrome in a string using algorithms")
    updated_state = agent.run(state)
    assert updated_state.retrieved_context is not None
    assert len(updated_state.retrieved_context) > 0
    assert "RetrievalAgent" in updated_state.action_history