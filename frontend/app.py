import os
import sys
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from schemas.state import TestCaseDetail
from execution.pytest_runner import run_custom_input_in_sandbox
from orchestrator.rl_orchestrator import MultiAgentCodingEnv
from orchestrator.deterministic_router import DeterministicRouter
from stable_baselines3 import PPO

app = FastAPI(title="Multi-Agent Coding System with RL Orchestration")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request & Response Schemas
class PipelineRequest(BaseModel):
    requirement: str
    test_code: Optional[str] = ""
    mode: str = "rl"  # "rl" or "baseline"

class AgentStepLog(BaseModel):
    step: int
    agent: str
    action_name: str
    reward: float
    passed: bool
    summary: str

class PipelineResponse(BaseModel):
    mode: str
    success: bool
    total_steps: int
    total_reward: float
    action_history: List[str]
    steps: List[AgentStepLog]
    code: str
    test_code: str
    review_score: float
    review_suggestions: List[str]
    test_passed: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_details: List[Dict[str, Any]]
    test_stdout: str
    test_stderr: str
    error_type: Optional[str] = None
    structured_requirement: Optional[Dict[str, Any]] = None
    plan: Optional[List[str]] = None

class CustomInputRequest(BaseModel):
    code: str
    custom_input: str

class CustomInputResponse(BaseModel):
    success: bool
    return_value: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    expression_evaluated: Optional[str] = None

@app.get("/api/problems")
def get_sample_problems():
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_requirements.json")
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.post("/api/run_custom_input", response_model=CustomInputResponse)
def execute_custom_input(req: CustomInputRequest):
    code = req.code.strip()
    custom_input = req.custom_input.strip()
    if not code:
        raise HTTPException(status_code=400, detail="No source code available to execute.")
    if not custom_input:
        raise HTTPException(status_code=400, detail="Please enter an input argument or function call.")

    result = run_custom_input_in_sandbox(code=code, custom_input=custom_input, timeout=5.0)
    return CustomInputResponse(
        success=result.get("success", False),
        return_value=result.get("return_value"),
        stdout=result.get("stdout", ""),
        stderr=result.get("stderr", ""),
        execution_time_ms=result.get("execution_time_ms", 0.0),
        error=result.get("error"),
        expression_evaluated=result.get("expression_evaluated")
    )

@app.post("/api/run", response_model=PipelineResponse)
def run_pipeline(req: PipelineRequest):
    requirement = req.requirement.strip()
    if not requirement:
        raise HTTPException(status_code=400, detail="Requirement cannot be empty.")

    if req.mode == "baseline":
        router = DeterministicRouter()
        state = router.run(requirement, req.test_code or "")
        
        steps = []
        for i, agent in enumerate(state.action_history, 1):
            steps.append(AgentStepLog(
                step=i,
                agent=agent,
                action_name=agent,
                reward=0.0,
                passed=bool(state.test_result and state.test_result.passed),
                summary=f"Executed {agent}"
            ))
            
        test_details_json = []
        if state.test_result and state.test_result.test_details:
            test_details_json = [t.model_dump() for t in state.test_result.test_details]

        return PipelineResponse(
            mode="baseline",
            success=bool(state.test_result and state.test_result.passed),
            total_steps=state.step_count,
            total_reward=state.total_reward,
            action_history=state.action_history,
            steps=steps,
            code=state.code or "",
            test_code=state.test_code or "",
            review_score=state.review_feedback.quality_score if state.review_feedback else 0.0,
            review_suggestions=state.review_feedback.suggestions if state.review_feedback else [],
            test_passed=bool(state.test_result and state.test_result.passed),
            total_tests=state.test_result.total_tests if state.test_result else 0,
            passed_tests=state.test_result.passed_tests if state.test_result else 0,
            failed_tests=state.test_result.failed_tests if state.test_result else 0,
            test_details=test_details_json,
            test_stdout=state.test_result.stdout if state.test_result else "",
            test_stderr=state.test_result.stderr if state.test_result else "",
            error_type=state.test_result.error_type if state.test_result else None,
            structured_requirement=state.structured_requirement.model_dump() if state.structured_requirement else None,
            plan=state.plan or []
        )

    # RL Orchestrator Mode
    env = MultiAgentCodingEnv(max_steps=8, simulated=False)
    obs, info = env.reset(options={"problem": {"requirement": requirement, "test_code": req.test_code or ""}})
    
    model_path = os.path.join(os.path.dirname(__file__), "..", "training", "models", "ppo_orchestrator.zip")
    model = None
    if os.path.exists(model_path):
        try:
            model = PPO.load(model_path)
        except Exception:
            pass

    done = False
    step = 0
    step_logs = []
    
    step_logs.append(AgentStepLog(
        step=1,
        agent="RequirementAnalyzer",
        action_name="RequirementAnalyzer",
        reward=0.0,
        passed=False,
        summary="Analyzed and structured requirements"
    ))

    while not done and step < 8:
        action_mask = env.get_action_mask()
        
        if model:
            action, _ = model.predict(obs, deterministic=True)
            action = int(action)
            if not action_mask[action]:
                if action_mask[0]: action = 0
                elif action_mask[2]: action = 2
                elif action_mask[4]: action = 4
                elif action_mask[5]: action = 5
                elif action_mask[6]: action = 6
                elif action_mask[3]: action = 3
                elif action_mask[7]: action = 7
                else: action = 7
        else:
            if action_mask[0]: action = 0
            elif action_mask[2]: action = 2
            elif action_mask[4]: action = 4
            elif action_mask[5]: action = 5
            elif action_mask[6]: action = 6
            elif action_mask[3]: action = 3
            elif action_mask[7]: action = 7
            else: action = 7

        action_name = env.ACTION_MAP.get(action, "Unknown")
        obs, reward, terminated, truncated, info = env.step(action)
        
        step_logs.append(AgentStepLog(
            step=step + 2,
            agent=action_name,
            action_name=action_name,
            reward=round(reward, 2),
            passed=bool(env.current_state.test_result and env.current_state.test_result.passed),
            summary=f"RL Orchestrator selected {action_name} (Reward: {reward:+.2f})"
        ))
        
        done = terminated or truncated
        step += 1

    final_state = env.current_state
    test_details_json = []
    if final_state.test_result and final_state.test_result.test_details:
        test_details_json = [t.model_dump() for t in final_state.test_result.test_details]

    return PipelineResponse(
        mode="rl",
        success=bool(final_state.test_result and final_state.test_result.passed),
        total_steps=final_state.step_count,
        total_reward=round(final_state.total_reward, 2),
        action_history=final_state.action_history,
        steps=step_logs,
        code=final_state.code or "",
        test_code=final_state.test_code or "",
        review_score=final_state.review_feedback.quality_score if final_state.review_feedback else 0.0,
        review_suggestions=final_state.review_feedback.suggestions if final_state.review_feedback else [],
        test_passed=bool(final_state.test_result and final_state.test_result.passed),
        total_tests=final_state.test_result.total_tests if final_state.test_result else 0,
        passed_tests=final_state.test_result.passed_tests if final_state.test_result else 0,
        failed_tests=final_state.test_result.failed_tests if final_state.test_result else 0,
        test_details=test_details_json,
        test_stdout=final_state.test_result.stdout if final_state.test_result else "",
        test_stderr=final_state.test_result.stderr if final_state.test_result else "",
        error_type=final_state.test_result.error_type if final_state.test_result else None,
        structured_requirement=final_state.structured_requirement.model_dump() if final_state.structured_requirement else None,
        plan=final_state.plan or []
    )

# Static files for Frontend UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Multi-Agent Coding System Frontend</h1>")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Multi-Agent RL Coding System Web UI")
    print("Open your browser at: http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
