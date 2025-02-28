#!/usr/bin/env python3
"""
Test for the Code Mutator module.

This tests the self-modifying code capability of the AIDevOS system.
"""

import os
import json
import pytest
from typing import Dict, Any, Optional, TYPE_CHECKING
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to sys.path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.deployment.code_mutator import (
    CodeMutator,
    GitHubIntegration,
    DurableObjectCodeMutator,
    CodeModificationSignature,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def mock_github_integration(mocker: "MockerFixture") -> MagicMock:
    """
    Create a mock GitHub integration.
    
    Args:
        mocker: Pytest mock fixture
        
    Returns:
        Mock GitHub integration
    """
    mock = mocker.patch("src.deployment.code_mutator.GitHubIntegration", autospec=True)
    mock_instance = mock.return_value
    mock_instance.create_branch.return_value = True
    mock_instance.commit_changes.return_value = True
    mock_instance.create_pull_request.return_value = "https://github.com/owner/repo/pull/123"
    return mock_instance


@pytest.fixture
def mock_dspy(mocker: "MockerFixture") -> Dict[str, MagicMock]:
    """
    Create mock DSPy components.
    
    Args:
        mocker: Pytest mock fixture
        
    Returns:
        Dictionary of mock DSPy components
    """
    mock_lm = mocker.patch("src.deployment.code_mutator.dspy.LM", autospec=True)
    mock_cot = mocker.patch("src.deployment.code_mutator.dspy.ChainOfThought", autospec=True)
    
    mock_cot_instance = mock_cot.return_value
    mock_cot_instance.return_value = MagicMock(
        modified_code="# Modified code\nprint('Hello, world!')",
        explanation="Added a hello world print statement",
    )
    
    return {
        "lm": mock_lm,
        "chain_of_thought": mock_cot,
        "cot_instance": mock_cot_instance,
    }


@pytest.fixture
def code_mutator(mock_github_integration: MagicMock, mock_dspy: Dict[str, MagicMock]) -> CodeMutator:
    """
    Create a CodeMutator with mocked dependencies.
    
    Args:
        mock_github_integration: Mock GitHub integration
        mock_dspy: Mock DSPy components
        
    Returns:
        CodeMutator instance
    """
    mutator = CodeMutator(
        github_token="fake-token",
        repository="owner/repo",
        base_branch="main",
    )
    
    # Use the mocks
    mutator.github = mock_github_integration
    mutator.code_modifier = mock_dspy["cot_instance"]
    
    return mutator


def test_github_integration_init() -> None:
    """Test the GitHubIntegration initialization."""
    # Test with explicit token
    github = GitHubIntegration(
        github_token="test-token",
        repository="test-owner/test-repo",
        base_branch="develop",
    )
    
    assert github.github_token == "test-token"
    assert github.repository == "test-owner/test-repo"
    assert github.base_branch == "develop"
    
    # Test with environment variable
    with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token"}):
        github = GitHubIntegration(
            repository="test-owner/test-repo",
        )
        assert github.github_token == "env-token"
        assert github.repository == "test-owner/test-repo"
        assert github.base_branch == "main"  # Default value


def test_code_mutator_init(mock_github_integration: MagicMock, mock_dspy: Dict[str, MagicMock]) -> None:
    """
    Test the CodeMutator initialization.
    
    Args:
        mock_github_integration: Mock GitHub integration
        mock_dspy: Mock DSPy components
    """
    with patch("src.deployment.code_mutator.GitHubIntegration") as mock_github_class:
        mock_github_class.return_value = mock_github_integration
        
        mutator = CodeMutator(
            github_token="test-token",
            repository="test-owner/test-repo",
            base_branch="develop",
            model_name="test-model",
        )
        
        # Check that GitHubIntegration was initialized correctly
        mock_github_class.assert_called_once_with(
            github_token="test-token",
            repository="test-owner/test-repo",
            base_branch="develop",
        )
        
        # Check that DSPy was initialized correctly
        mock_dspy["lm"].assert_called_once_with(model="test-model")
        mock_dspy["chain_of_thought"].assert_called_once_with(CodeModificationSignature)


def test_mutate_without_deploy(code_mutator: CodeMutator) -> None:
    """
    Test the mutate method without auto-deploy.
    
    Args:
        code_mutator: CodeMutator instance
    """
    # Mock open to avoid reading from actual file
    with patch("builtins.open", mock_open(read_data="# Original code")):
        result = code_mutator.mutate(
            prompt="Add a hello world print statement",
            file_path="/path/to/file.py",
            auto_deploy=False,
        )
    
    # Check the result
    assert result["status"] == "success"
    assert result["prompt"] == "Add a hello world print statement"
    assert result["file_path"] == "/path/to/file.py"
    assert result["modified_code"] == "# Modified code\nprint('Hello, world!')"
    assert result["explanation"] == "Added a hello world print statement"
    assert not result["deployed"]
    
    # Check that GitHub methods were not called
    code_mutator.github.create_branch.assert_not_called()
    code_mutator.github.commit_changes.assert_not_called()
    code_mutator.github.create_pull_request.assert_not_called()


def test_mutate_with_deploy(code_mutator: CodeMutator) -> None:
    """
    Test the mutate method with auto-deploy.
    
    Args:
        code_mutator: CodeMutator instance
    """
    # Mock open to avoid reading from actual file
    with patch("builtins.open", mock_open(read_data="# Original code")):
        # Mock datetime to get a predictable branch name
        with patch("src.deployment.code_mutator.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20250228024242"
            
            result = code_mutator.mutate(
                prompt="Add a hello world print statement",
                file_path="/path/to/file.py",
                auto_deploy=True,
            )
    
    # Check the result
    assert result["status"] == "success"
    assert result["prompt"] == "Add a hello world print statement"
    assert result["file_path"] == "/path/to/file.py"
    assert result["modified_code"] == "# Modified code\nprint('Hello, world!')"
    assert result["explanation"] == "Added a hello world print statement"
    assert result["deployed"]
    assert result["branch_name"] == "feature/ai-mutation-20250228024242"
    assert result["pr_url"] == "https://github.com/owner/repo/pull/123"
    
    # Check that GitHub methods were called
    code_mutator.github.create_branch.assert_called_once_with("feature/ai-mutation-20250228024242")
    code_mutator.github.commit_changes.assert_called_once_with(
        file_path="/path/to/file.py",
        content="# Modified code\nprint('Hello, world!')",
        commit_message="AI-generated mutation: Add a hello world print statement",
    )
    code_mutator.github.create_pull_request.assert_called_once_with(
        branch_name="feature/ai-mutation-20250228024242",
        title="AI-generated mutation: Add a hello world print statement...",
        description="This PR was automatically generated based on the following prompt:\n\nAdd a hello world print statement\n\n## Explanation\n\nAdded a hello world print statement",
    )


def test_handle_mutate_request_missing_prompt() -> None:
    """Test handling a mutate request with missing prompt."""
    do_mutator = DurableObjectCodeMutator(MagicMock())
    
    result = do_mutator.handle_mutate_request({
        "file_path": "/path/to/file.py",
    })
    
    assert result["status"] == "error"
    assert result["error"] == "Missing prompt in request body"
    assert result["code"] == 400


def test_handle_mutate_request_missing_file_path() -> None:
    """Test handling a mutate request with missing file path."""
    do_mutator = DurableObjectCodeMutator(MagicMock())
    
    result = do_mutator.handle_mutate_request({
        "prompt": "Add a hello world print statement",
    })
    
    assert result["status"] == "error"
    assert result["error"] == "Missing file_path in request body"
    assert result["code"] == 400


def test_handle_mutate_request_success() -> None:
    """Test handling a successful mutate request."""
    mock_code_mutator = MagicMock()
    mock_code_mutator.mutate.return_value = {
        "status": "success",
        "prompt": "Add a hello world print statement",
        "file_path": "/path/to/file.py",
        "modified_code": "# Modified code\nprint('Hello, world!')",
        "explanation": "Added a hello world print statement",
        "deployed": True,
        "branch_name": "feature/ai-mutation-20250228024242",
        "pr_url": "https://github.com/owner/repo/pull/123",
    }
    
    do_mutator = DurableObjectCodeMutator(mock_code_mutator)
    
    result = do_mutator.handle_mutate_request({
        "prompt": "Add a hello world print statement",
        "file_path": "/path/to/file.py",
        "auto_deploy": True,
    })
    
    assert result["status"] == "success"
    assert result["prompt"] == "Add a hello world print statement"
    assert result["file_path"] == "/path/to/file.py"
    assert result["modified_code"] == "# Modified code\nprint('Hello, world!')"
    assert result["explanation"] == "Added a hello world print statement"
    assert result["deployed"]
    assert result["branch_name"] == "feature/ai-mutation-20250228024242"
    assert result["pr_url"] == "https://github.com/owner/repo/pull/123"
    
    mock_code_mutator.mutate.assert_called_once_with(
        prompt="Add a hello world print statement",
        file_path="/path/to/file.py",
        auto_deploy=True,
    )


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
