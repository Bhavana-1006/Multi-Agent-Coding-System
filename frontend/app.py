import os
import sys
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from schemas.state import TestCaseDetail, ProjectState
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

# Feature & Action Metadata for RL Explainability
RL_FEATURE_LABELS = [
    "Requirements Analyzed",
    "Plan Formulated",
    "Context Retrieved",
    "Code Synthesized",
    "Code Reviewed",
    "Quality Score [0-1]",
    "Tests Present",
    "All Tests Passed",
    "Test Pass Ratio",
    "Error Diagnostic Done",
    "Step Progression",
    "Recent Self-Repair",
    "Repair Attempt Count",
    "Syntax Error Detected",
    "Problem Difficulty"
]

RL_ACTION_LABELS = [
    "PlanningAgent",
    "RetrievalAgent",
    "CodingAgent",
    "ReviewAgent",
    "TestingAgent",
    "ErrorAnalysisAgent",
    "SelfRepairAgent",
    "Terminate"
]

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
    retrieved_context: Optional[str] = None
    error_analysis: Optional[str] = None
    observation_vector: Optional[List[float]] = None
    action_mask: Optional[List[bool]] = None

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

def build_pipeline_response(
    state: ProjectState,
    mode: str,
    steps: List[AgentStepLog],
    observation_vector: Optional[List[float]] = None,
    action_mask: Optional[List[bool]] = None
) -> PipelineResponse:
    test_details_json = []
    if state.test_result and state.test_result.test_details:
        test_details_json = [t.model_dump() for t in state.test_result.test_details]

    return PipelineResponse(
        mode=mode,
        success=bool(state.test_result and state.test_result.passed),
        total_steps=state.step_count,
        total_reward=round(state.total_reward, 2),
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
        plan=state.plan or [],
        retrieved_context=state.retrieved_context or "",
        error_analysis=state.error_analysis or "",
        observation_vector=observation_vector if observation_vector is not None else state.to_feature_vector().tolist(),
        action_mask=action_mask or []
    )

@app.get("/api/config")
def get_system_config():
    """Returns active LLM backend provider status, RL model state, and benchmark stats."""
    from llm.client import LLMClient
    client = LLMClient()
    providers = []
    if client.groq_client:
        model_name = getattr(client, "groq_model", "qwen/qwen3.8-27b")
        providers.append({"name": "Groq Cloud", "active": True, "model": model_name, "type": "free_cloud", "desc": "14,400 Free Req/Day"})
    if client.gemini_client:
        providers.append({"name": "Google Gemini", "active": True, "model": "gemini-2.5-flash", "type": "cloud", "desc": "Multimodal Flash"})
    if client.openrouter_client:
        providers.append({"name": "OpenRouter", "active": True, "model": "deepseek-r1", "type": "cloud", "desc": "Multi-model router"})
    if client.openai_client:
        providers.append({"name": "OpenAI", "active": True, "model": "gpt-4o", "type": "cloud", "desc": "GPT-4o"})
    if client.ollama_client:
        providers.append({"name": "Local Ollama", "active": True, "model": "local", "type": "offline", "desc": "Offline Private"})
    if not providers:
        providers.append({"name": "Adaptive Offline Engine", "active": True, "model": "rule-based", "type": "offline", "desc": "Zero-Cost Synthetic Fallback"})

    model_path = os.path.join(os.path.dirname(__file__), "..", "training", "models", "ppo_orchestrator.zip")
    rl_model_available = os.path.exists(model_path)

    dataset_path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_requirements.json")
    problem_count = 0
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                problem_count = len(json.load(f))
        except Exception:
            pass

    return {
        "providers": providers,
        "active_provider": providers[0]["name"] if providers else "Adaptive Offline Engine",
        "active_model": providers[0]["model"] if providers else "rule-based",
        "rl_policy_loaded": rl_model_available,
        "total_benchmark_problems": problem_count,
        "max_rl_steps": 8,
        "action_space_size": 8,
        "observation_dim": 15,
        "feature_labels": RL_FEATURE_LABELS,
        "action_labels": RL_ACTION_LABELS
    }

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
            
        return build_pipeline_response(state, "baseline", steps)

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
                for fallback in [0, 2, 4, 5, 6, 3, 7]:
                    if action_mask[fallback]:
                        action = fallback
                        break
        else:
            action = 7
            for fallback in [0, 2, 4, 5, 6, 3, 7]:
                if action_mask[fallback]:
                    action = fallback
                    break

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
    return build_pipeline_response(
        final_state,
        "rl",
        step_logs,
        observation_vector=final_state.to_feature_vector().tolist(),
        action_mask=env.get_action_mask().tolist()
    )

@app.post("/api/run/stream")
def run_pipeline_stream(req: PipelineRequest):
    """Server-Sent Events endpoint streaming real-time agent execution and RL decisions."""
    requirement = req.requirement.strip()
    if not requirement:
        raise HTTPException(status_code=400, detail="Requirement cannot be empty.")

    def event_stream():
        try:
            yield f"data: {json.dumps({'event': 'started', 'mode': req.mode})}\n\n"

            if req.mode == "baseline":
                state = ProjectState(raw_requirement=requirement, test_code=req.test_code or "")
                router = DeterministicRouter()
                steps = []

                def run_and_stream_step(step_idx: int, agent_name: str, runner_fn, desc: str):
                    nonlocal state
                    yield f"data: {json.dumps({'event': 'step_start', 'step': step_idx, 'agent': agent_name, 'action_name': agent_name, 'observation_vector': state.to_feature_vector().tolist()})}\n\n"
                    state = runner_fn(state)
                    passed = bool(state.test_result and state.test_result.passed)
                    step_log = AgentStepLog(
                        step=step_idx,
                        agent=agent_name,
                        action_name=agent_name,
                        reward=0.0,
                        passed=passed,
                        summary=desc
                    )
                    steps.append(step_log)
                    intermediate = {
                        'has_code': bool(state.code),
                        'has_plan': bool(state.plan and len(state.plan) > 0),
                        'code': state.code or "",
                        'test_passed': passed,
                        'review_score': state.review_feedback.quality_score if state.review_feedback else 0.0,
                        'total_reward': 0.0,
                        'structured_requirement': state.structured_requirement.model_dump() if state.structured_requirement else None,
                        'plan': state.plan or [],
                        'retrieved_context': state.retrieved_context or "",
                        'error_analysis': state.error_analysis or ""
                    }
                    yield f"data: {json.dumps({'event': 'step_done', 'step': step_idx, 'agent': agent_name, 'reward': 0.0, 'total_reward': 0.0, 'summary': desc, 'intermediate': intermediate})}\n\n"

                # 1. Req Analyzer
                yield from run_and_stream_step(1, "RequirementAnalyzer", router.req_analyzer.run, "Extracted constraints, edge cases and specification")
                # 2. Planner
                yield from run_and_stream_step(2, "PlanningAgent", router.planner.run, "Formulated architectural implementation plan")
                # 3. Retriever
                yield from run_and_stream_step(3, "RetrievalAgent", router.retriever.run, "Queried algorithm knowledge store")
                # 4. Coder
                yield from run_and_stream_step(4, "CodingAgent", router.coder.run, "Synthesized code solution")
                # 5. Reviewer
                yield from run_and_stream_step(5, "ReviewAgent", router.reviewer.run, "Evaluated quality score and standards")
                # 6. Tester
                yield from run_and_stream_step(6, "TestingAgent", router.tester.run, "Executed assertions in sandbox")

                # 7. Self-repair loop if needed
                attempts = 0
                step_idx = 7
                while state.test_result and not state.test_result.passed and attempts < router.max_repair_attempts:
                    attempts += 1
                    yield from run_and_stream_step(step_idx, "ErrorAnalysisAgent", router.error_analyzer.run, f"Diagnosed test failure trace (Attempt {attempts})")
                    step_idx += 1
                    yield from run_and_stream_step(step_idx, "SelfRepairAgent", router.repairer.run, f"Patched code implementation (Attempt {attempts})")
                    step_idx += 1
                    yield from run_and_stream_step(step_idx, "TestingAgent", router.tester.run, f"Re-tested patched code in sandbox (Attempt {attempts})")
                    step_idx += 1

                final_resp = build_pipeline_response(state, "baseline", steps)
                yield f"data: {json.dumps({'event': 'complete', 'data': final_resp.model_dump()})}\n\n"
                return

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

            step_logs = []
            
            # Step 1: RequirementAnalyzer
            yield f"data: {json.dumps({'event': 'step_start', 'step': 1, 'agent': 'RequirementAnalyzer', 'action_name': 'RequirementAnalyzer', 'observation_vector': env.current_state.to_feature_vector().tolist(), 'action_mask': env.get_action_mask().tolist()})}\n\n"
            step_logs.append(AgentStepLog(
                step=1,
                agent="RequirementAnalyzer",
                action_name="RequirementAnalyzer",
                reward=0.0,
                passed=False,
                summary="Analyzed and structured requirements"
            ))
            yield f"data: {json.dumps({'event': 'step_done', 'step': 1, 'agent': 'RequirementAnalyzer', 'reward': 0.0, 'total_reward': 0.0, 'summary': 'Analyzed and structured requirements', 'intermediate': {'structured_requirement': env.current_state.structured_requirement.model_dump() if env.current_state.structured_requirement else None}})}\n\n"

            done = False
            step = 0
            while not done and step < 8:
                action_mask = env.get_action_mask()
                obs_vec = env.current_state.to_feature_vector().tolist()

                if model:
                    action, _ = model.predict(obs, deterministic=True)
                    action = int(action)
                    if not action_mask[action]:
                        for fallback in [0, 2, 4, 5, 6, 3, 7]:
                            if action_mask[fallback]:
                                action = fallback
                                break
                else:
                    action = 7
                    for fallback in [0, 2, 4, 5, 6, 3, 7]:
                        if action_mask[fallback]:
                            action = fallback
                            break

                action_name = env.ACTION_MAP.get(action, "Unknown")

                # Send step_start with state observation vector and action mask
                yield f"data: {json.dumps({'event': 'step_start', 'step': step + 2, 'agent': action_name, 'action_name': action_name, 'action_idx': action, 'action_mask': action_mask.tolist(), 'observation_vector': obs_vec})}\n\n"

                obs, reward, terminated, truncated, info = env.step(action)

                passed = bool(env.current_state.test_result and env.current_state.test_result.passed)
                step_log = AgentStepLog(
                    step=step + 2,
                    agent=action_name,
                    action_name=action_name,
                    reward=round(reward, 2),
                    passed=passed,
                    summary=f"RL Orchestrator selected {action_name} (Reward: {reward:+.2f})"
                )
                step_logs.append(step_log)

                intermediate = {
                    'has_code': bool(env.current_state.code),
                    'has_plan': bool(env.current_state.plan and len(env.current_state.plan) > 0),
                    'code': env.current_state.code or "",
                    'test_passed': passed,
                    'review_score': env.current_state.review_feedback.quality_score if env.current_state.review_feedback else 0.0,
                    'total_reward': round(env.current_state.total_reward, 2),
                    'plan': env.current_state.plan or [],
                    'retrieved_context': env.current_state.retrieved_context or "",
                    'error_analysis': env.current_state.error_analysis or ""
                }
                if env.current_state.structured_requirement:
                    intermediate['structured_requirement'] = env.current_state.structured_requirement.model_dump()

                yield f"data: {json.dumps({'event': 'step_done', 'step': step + 2, 'agent': action_name, 'action_name': action_name, 'reward': round(reward, 2), 'total_reward': round(env.current_state.total_reward, 2), 'summary': step_log.summary, 'intermediate': intermediate})}\n\n"

                done = terminated or truncated
                step += 1

            final_state = env.current_state
            final_resp = build_pipeline_response(
                final_state,
                "rl",
                step_logs,
                observation_vector=final_state.to_feature_vector().tolist(),
                action_mask=env.get_action_mask().tolist()
            )
            yield f"data: {json.dumps({'event': 'complete', 'data': final_resp.model_dump()})}\n\n"

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'event': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Static files for Frontend UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return HTMLResponse("<h1>Multi-Agent Coding System Frontend</h1>")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Multi-Agent RL Coding System Web UI")
    print("Open your browser at: http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)

