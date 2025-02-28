#!/usr/bin/env python3
"""
Tests for the DSPy integration with AIDevOS.

This module contains tests to verify that the DSPy integration works correctly.
"""

import os
import sys
import json
import pytest
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import logging

# Set up the path to include the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local imports
from src.agents.dspy_modules import PMAgentModule
from src.agents.dspy_agent import DSPyPMAgent
from src.config.dspy_config import DSPyConfig

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def mock_environment(monkeypatch: "MonkeyPatch") -> None:
    """
    Set up a mock environment for testing.
    
    Args:
        monkeypatch: PyTest monkeypatch fixture.
    """
    # Mock OpenAI API key for testing
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-for-openai")
    
    # Mock other environment variables as needed


@pytest.fixture
def dspy_config() -> DSPyConfig:
    """
    Create a DSPyConfig instance for testing.
    
    Returns:
        A DSPyConfig instance.
    """
    return DSPyConfig()


def test_pm_agent_module() -> None:
    """Test that the PM Agent module can be instantiated."""
    module = PMAgentModule()
    assert module is not None, "PM Agent module should be instantiated"


def test_dspy_pm_agent() -> None:
    """Test that the DSPy-enabled PM Agent can be instantiated."""
    agent = DSPyPMAgent("test_pm_agent")
    assert agent is not None, "DSPy PM Agent should be instantiated"
    assert agent.role == "PM", "Agent role should be PM"
    assert agent.module is not None, "Agent should have a DSPy module"


@pytest.mark.parametrize(
    "task_type, expected_result", 
    [
        ("requirements_analysis", {"status": "success"}),
        ("architecture_design", {"name": "System Architecture"}),
    ]
)
def test_mock_pm_agent_process_task(
    task_type: str, 
    expected_result: Dict[str, Any],
    mocker: "MockerFixture"
) -> None:
    """
    Test that the PM Agent can process tasks with mocked responses.
    
    Args:
        task_type: Type of task to process.
        expected_result: Expected result keys.
        mocker: PyTest mocker fixture.
    """
    # Create a PM Agent
    agent = DSPyPMAgent("test_pm_agent")
    
    # Mock the DSPy module's forward method
    mock_result = {
        "requirements_analysis": {
            "status": "success",
            "requirements": {
                "name": "Test Project",
                "description": "A test project"
            }
        },
        "architecture_design": {
            "name": "System Architecture",
            "components": [
                {"name": "Component1", "description": "A test component"}
            ]
        }
    }[task_type]
    
    mocker.patch.object(
        agent.module, 
        "forward", 
        return_value=mock_result
    )
    
    # Create a task
    task = {
        "type": task_type,
        "description": "Test task"
    }
    
    # Process the task
    import asyncio
    result = asyncio.run(agent.process_task(task))
    
    # Check the result
    for key in expected_result:
        assert key in result, f"Result should contain {key}"


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), 
    reason="OpenAI API key not found in environment"
)
def test_live_requirements_analysis() -> None:
    """
    Test that the PM Agent can analyze requirements with a live LLM.
    
    This test requires a valid OpenAI API key.
    """
    # Create a PM Agent
    agent = DSPyPMAgent("test_pm_agent")
    
    # Create a requirements analysis task
    task = {
        "type": "requirements_analysis",
        "description": "Create a simple to-do list app with task prioritization"
    }
    
    # Process the task
    import asyncio
    result = asyncio.run(agent.process_task(task))
    
    # Check the result
    assert "status" in result, "Result should contain status"
    assert "requirements" in result, "Result should contain requirements"
    
    # Print the result for inspection
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pytest.main(["-v", __file__])
