"""Integration tests for Person 4's agent workflow."""
import pytest
import requests

def is_ollama_running():
    try:
        response = requests.get("http://localhost:11434", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

SKIP_IF_NO_OLLAMA = pytest.mark.skipif(
    not is_ollama_running(),
    reason="Ollama is not running locally"
)

class TestAgentWorkflow:
    
    def test_import(self):
        """agent_workflow.py is importable."""
        try:
            from scripts.agent_workflow import run_agent
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
    
    @SKIP_IF_NO_OLLAMA
    def test_run_agent_returns_string(self):
        """run_agent returns a string answer."""
        try:
            from scripts.agent_workflow import run_agent
            result = run_agent("How many EVs are in King County?")
            assert isinstance(result, str)
            assert len(result) > 10  # Should be more than just "error"
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
    
    @SKIP_IF_NO_OLLAMA
    def test_router_data_classification(self):
        """Router correctly classifies data questions."""
        try:
            from scripts.agent_workflow import route_question
            result = route_question("How many EVs in King County?")
            assert result in ("data", "both")
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
    
    @SKIP_IF_NO_OLLAMA
    def test_router_policy_classification(self):
        """Router correctly classifies policy questions."""
        try:
            from scripts.agent_workflow import route_question
            result = route_question("What is the CAFV tax credit eligibility?")
            assert result in ("policy", "both")
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
