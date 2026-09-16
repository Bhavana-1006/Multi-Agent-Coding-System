import pytest
import json
from fastapi.testclient import TestClient
from frontend.app import app

client = TestClient(app)

def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Multi-Agent Coding System" in response.text
    assert "theme-toggle-btn" in response.text
    assert "view-landing" in response.text
    assert "view-studio" in response.text
    assert "navigateTo('studio')" in response.text
    assert "navigateTo('landing')" in response.text
    assert "problem-modal" in response.text

def test_api_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "active_provider" in data
    assert "feature_labels" in data
    assert len(data["feature_labels"]) == 15
    assert "action_labels" in data
    assert len(data["action_labels"]) == 8

def test_api_problems():
    response = client.get("/api/problems")
    assert response.status_code == 200
    problems = response.json()
    assert isinstance(problems, list)
    assert len(problems) > 0
    assert "name" in problems[0]
    assert "requirement" in problems[0]

def test_run_custom_input():
    code = "def is_palindrome(s):\n    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n    return cleaned == cleaned[::-1]\n"
    response = client.post("/api/run_custom_input", json={
        "code": code,
        "custom_input": "is_palindrome('racecar')"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["return_value"] == "True"

def test_run_custom_input_failure():
    code = "def broken(): raise ValueError('intentional error')"
    response = client.post("/api/run_custom_input", json={
        "code": code,
        "custom_input": "broken()"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "ValueError" in (data["error"] or data["stderr"])

def test_studio_workspace_redesign():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # 1. Congested elements removed from main view
    assert "Preset Templates:" not in html
    assert "metric-tests-ratio" not in html
    assert "workspace-tabs" not in html
    assert "Cumulative Reward" not in html

    # 2. Conversational elements present
    assert "What do you want to build?" in html
    assert "Describe your coding requirement in plain English." in html
    assert "req-input-empty" in html
    assert "studio-empty-state" in html
    assert "studio-active-state" in html
    assert "req-bubble-card" in html
    assert "code-editor-card" in html
    assert "Try your own input" in html
    assert "playground-input" in html
    assert "playground-run-btn" in html
    assert "custom-testcases-card" in html
    assert "settings-drawer" in html
    assert "recent-requests-list" in html
    assert "studio-sidebar" in html

