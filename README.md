# AI-Powered Multi-Agent Coding System with RL Orchestration

An autonomous Multi-Agent Software Development system that dynamically orchestrates specialized coding agents using Reinforcement Learning (PPO) and Actor-Critic decision policies.

---

## 🌟 Key Features

1. **Reinforcement Learning Orchestrator (PPO)**:
   - Uses a continuous 15-dimensional observation vector and 8 discrete action spaces.
   - Learns optimal, minimal-cost agent dispatch paths rather than fixed sequential pipelines.
   - Enforces strict **Action Masking** to eliminate infinite loops and illegal transitions.

2. **Full Agent Pool**:
   - `RequirementAnalyzerAgent`: Analyzes natural language specifications, constraints, and edge cases.
   - `PlanningAgent`: Generates modular implementation roadmaps.
   - `RetrievalAgent`: RAG vector store over algorithmic documentation and design patterns.
   - `CodingAgent`: High-performance code synthesis.
   - `TestingAgent`: Dynamic test generator & isolated subprocess sandbox runner.
   - `ReviewAgent`: Code quality, syntax standard, and time-complexity reviewer.
   - `ErrorAnalysisAgent`: Diagnostic debugger for stack trace analysis.
   - `SelfRepairAgent`: Autonomous bug patcher.

3. **Multi-Provider LLM Engine**:
   - **Groq Cloud (14,400 Free Requests/Day)**: Fast inference with `qwen/qwen3.8-27b`.
   - **Google Gemini & OpenAI**: Direct cloud model support.
   - **Local Ollama**: 100% offline, unlimited local execution.
   - **Adaptive Offline Engine**: Instant zero-cost fallback for offline environments.

4. **Modern Developer-Focused Web UI**:
   - Sophisticated plum (`#17121C`), purple (`#9B5DE5`), and coral (`#FF6B6B`) aesthetic with modular styling.
   - User-first landing page with interactive coding prompt, visual workflow stepper, and mock workspace preview.
   - Studio Workspace featuring live Server-Sent Events (SSE) streaming, syntax-highlighted editor, subprocess sandbox test runner, quality review meter, and custom input playground.

---

## 🚀 Quick Start

### 1. Run the Interactive Web Frontend
```powershell
.\venv\Scripts\python.exe frontend/app.py
```
Open your browser at **`http://localhost:8000`** to access the interactive dashboard.

---

### 2. Run via CLI
```powershell
# Run with RL Orchestration
.\venv\Scripts\python.exe main.py --mode rl --req "Write a function is_prime(n) to check prime numbers."

# Run with Deterministic Baseline
.\venv\Scripts\python.exe main.py --mode baseline --req "Write a function is_prime(n) to check prime numbers."
```

---

### 3. Train & Evaluate RL Policy
```powershell
# Train PPO policy for 3,000 timesteps (< 3 seconds)
.\venv\Scripts\python.exe training/train_ppo.py --timesteps 3000

# Benchmark RL Orchestrator vs Fixed Baseline
.\venv\Scripts\python.exe training/evaluate_policy.py

# Generate comparison charts
.\venv\Scripts\python.exe training/plot_experiments.py
```
Charts are saved to `logs/benchmark_comparison.png`.

---

### 4. Run Test Suite
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```
