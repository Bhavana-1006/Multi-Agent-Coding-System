import pytest
import numpy as np
from orchestrator.rl_orchestrator import MultiAgentCodingEnv
from execution.pytest_runner import run_tests_in_sandbox

def test_sandbox_execution_success():
    code = "def multiply(a, b): return a * b"
    test_code = "assert multiply(3, 4) == 12\nassert multiply(-2, 5) == -10"
    res = run_tests_in_sandbox(code, test_code)
    assert res.passed is True
    assert res.failed_tests == 0

def test_sandbox_execution_failure():
    code = "def multiply(a, b): return a + b"  # Buggy implementation
    test_code = "assert multiply(3, 4) == 12"
    res = run_tests_in_sandbox(code, test_code)
    assert res.passed is False
    assert res.error_type == "AssertionError"

def test_env_observation_space():
    env = MultiAgentCodingEnv(max_steps=5)
    obs, info = env.reset()
    assert obs.shape == (12,)
    assert isinstance(info, dict)
    assert env.action_space.n == 8
