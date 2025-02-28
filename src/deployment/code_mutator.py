#!/usr/bin/env python3
"""
Code Mutator for AIDevOS.

This module provides functionality for Durable Objects to self-modify their own code
based on AI prompts and deploy the changes using version control integration.
"""

import logging
import time
import json
import os
import uuid
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime

import dspy
from dspy.teleprompt import BootstrapFewShot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.code_mutator")


class CodeModificationSignature(dspy.Signature):
    """Signature for code modification based on a prompt."""
    
    prompt = dspy.InputField(desc="The prompt describing what should be changed or improved")
    current_code = dspy.InputField(desc="The current implementation of the code")
    
    modified_code = dspy.OutputField(desc="The modified implementation based on the prompt")
    explanation = dspy.OutputField(desc="Explanation of the changes made")


class GitHubIntegration:
    """
    Integration with GitHub for version control and deployment.
    
    This class handles creating new branches, committing changes, and
    submitting pull requests for code modifications.
    """
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        repository: str = "owner/repo",
        base_branch: str = "main",
    ):
        """
        Initialize the GitHub integration.
        
        Args:
            github_token: GitHub personal access token
            repository: Repository in the format "owner/repo"
            base_branch: Base branch to branch from
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        if not self.github_token:
            logger.warning("GitHub token not provided, some operations may fail")
        
        self.repository = repository
        self.base_branch = base_branch
        logger.info(f"GitHub integration initialized for repository {repository}")
    
    def create_branch(self, branch_name: str) -> bool:
        """
        Create a new branch in the repository.
        
        Args:
            branch_name: Name of the branch to create
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Creating branch {branch_name} in {self.repository}")
        
        # This is a placeholder implementation
        # In a real implementation, this would use the GitHub API
        # or git CLI to create a branch
        
        try:
            # Example using git CLI
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "push", "--set-upstream", "origin", branch_name],
                check=True,
                capture_output=True,
                env={"GITHUB_TOKEN": self.github_token, **os.environ},
            )
            logger.info(f"Branch {branch_name} created successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating branch: {e.stderr.decode('utf-8')}")
            return False
    
    def commit_changes(
        self, 
        file_path: str, 
        content: str, 
        commit_message: str
    ) -> bool:
        """
        Commit changes to a file in the repository.
        
        Args:
            file_path: Path to the file to modify
            content: New content for the file
            commit_message: Commit message
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Committing changes to {file_path} in {self.repository}")
        
        try:
            # Write content to the file
            with open(file_path, "w") as f:
                f.write(content)
            
            # Commit the changes
            subprocess.run(
                ["git", "add", file_path],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "push"],
                check=True,
                capture_output=True,
                env={"GITHUB_TOKEN": self.github_token, **os.environ},
            )
            logger.info(f"Changes to {file_path} committed successfully")
            return True
        except (subprocess.CalledProcessError, IOError) as e:
            logger.error(f"Error committing changes: {str(e)}")
            return False
    
    def create_pull_request(
        self,
        branch_name: str,
        title: str,
        description: str,
    ) -> Optional[str]:
        """
        Create a pull request in the repository.
        
        Args:
            branch_name: Name of the branch to create the PR from
            title: Title of the PR
            description: Description of the PR
            
        Returns:
            PR URL if successful, None otherwise
        """
        logger.info(f"Creating PR from {branch_name} to {self.base_branch} in {self.repository}")
        
        # This is a placeholder implementation
        # In a real implementation, this would use the GitHub API
        
        try:
            # Example using GitHub CLI
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", title,
                    "--body", description,
                    "--base", self.base_branch,
                    "--head", branch_name,
                ],
                check=True,
                capture_output=True,
                env={"GITHUB_TOKEN": self.github_token, **os.environ},
            )
            pr_url = result.stdout.decode("utf-8").strip()
            logger.info(f"PR created successfully: {pr_url}")
            return pr_url
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating PR: {e.stderr.decode('utf-8')}")
            return None


class CodeMutator:
    """
    Code Mutator for AIDevOS.
    
    This class provides functionality for Durable Objects to self-modify their own code
    based on AI prompts and deploy the changes using version control integration.
    """
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        repository: str = "owner/repo",
        base_branch: str = "main",
        model_name: str = "gpt-4",
    ):
        """
        Initialize the Code Mutator.
        
        Args:
            github_token: GitHub personal access token
            repository: Repository in the format "owner/repo"
            base_branch: Base branch to branch from
            model_name: Name of the LLM model to use
        """
        self.github = GitHubIntegration(
            github_token=github_token,
            repository=repository,
            base_branch=base_branch,
        )
        
        # Initialize DSPy for code modification
        self.lm = dspy.LM(model=model_name)
        self.code_modifier = dspy.ChainOfThought(CodeModificationSignature)
        
        logger.info("Code Mutator initialized")
    
    def mutate(
        self,
        prompt: str,
        file_path: str,
        auto_deploy: bool = False,
    ) -> Dict[str, Any]:
        """
        Mutate code based on a prompt.
        
        Args:
            prompt: Prompt describing the desired changes
            file_path: Path to the file to modify
            auto_deploy: Whether to automatically deploy the changes
            
        Returns:
            Dictionary with results of the mutation
        """
        logger.info(f"Mutating code in {file_path} based on prompt: {prompt}")
        
        try:
            # Read the current code
            with open(file_path, "r") as f:
                current_code = f.read()
            
            # Generate modified code
            result = self.code_modifier(
                prompt=prompt,
                current_code=current_code,
            )
            
            modified_code = result.modified_code
            explanation = result.explanation
            
            # Generate branch name and commit message
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            branch_name = f"feature/ai-mutation-{timestamp}"
            commit_message = f"AI-generated mutation: {prompt}"
            
            # Create branch and commit changes
            mutation_result = {
                "status": "success",
                "prompt": prompt,
                "explanation": explanation,
                "file_path": file_path,
                "branch_name": branch_name,
                "modified_code": modified_code,
                "deployed": False,
            }
            
            if auto_deploy:
                # Create branch
                if not self.github.create_branch(branch_name):
                    mutation_result["status"] = "error"
                    mutation_result["error"] = "Failed to create branch"
                    return mutation_result
                
                # Commit changes
                if not self.github.commit_changes(
                    file_path=file_path,
                    content=modified_code,
                    commit_message=commit_message,
                ):
                    mutation_result["status"] = "error"
                    mutation_result["error"] = "Failed to commit changes"
                    return mutation_result
                
                # Create PR
                pr_url = self.github.create_pull_request(
                    branch_name=branch_name,
                    title=f"AI-generated mutation: {prompt[:50]}...",
                    description=f"This PR was automatically generated based on the following prompt:\n\n{prompt}\n\n## Explanation\n\n{explanation}",
                )
                
                if pr_url:
                    mutation_result["deployed"] = True
                    mutation_result["pr_url"] = pr_url
                else:
                    mutation_result["status"] = "error"
                    mutation_result["error"] = "Failed to create PR"
            
            return mutation_result
        
        except Exception as e:
            logger.error(f"Error mutating code: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "prompt": prompt,
                "file_path": file_path,
            }


class DurableObjectCodeMutator:
    """
    Durable Object interface for the Code Mutator.
    
    This class provides an interface for Durable Objects to use the Code Mutator
    for self-modifying their own code based on AI prompts.
    """
    
    def __init__(
        self,
        code_mutator: Optional[CodeMutator] = None,
    ):
        """
        Initialize the Durable Object Code Mutator.
        
        Args:
            code_mutator: Code Mutator instance
        """
        self.code_mutator = code_mutator or CodeMutator()
        
        logger.info("Durable Object Code Mutator initialized")
    
    def handle_mutate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request to mutate code.
        
        Args:
            request_data: Request data containing prompt and other parameters
            
        Returns:
            Response data with results of the mutation
        """
        prompt = request_data.get("prompt")
        if not prompt:
            return {
                "status": "error",
                "error": "Missing prompt in request body",
                "code": 400,
            }
        
        file_path = request_data.get("file_path")
        if not file_path:
            return {
                "status": "error",
                "error": "Missing file_path in request body",
                "code": 400,
            }
        
        auto_deploy = request_data.get("auto_deploy", False)
        auto_merge = request_data.get("auto_merge", False)
        
        # Mutate the code
        result = self.code_mutator.mutate(
            prompt=prompt,
            file_path=file_path,
            auto_deploy=auto_deploy,
        )
        
        return result


def setup_routes(app, code_mutator: Optional[CodeMutator] = None):
    """
    Set up the routes for the Code Mutator API.
    
    Args:
        app: The application object (e.g., FastAPI, Flask)
        code_mutator: Code Mutator instance
    """
    do_code_mutator = DurableObjectCodeMutator(code_mutator)
    
    @app.post("/mutate")
    async def mutate(request):
        """
        Handle a request to mutate code.
        
        Args:
            request: HTTP request object
            
        Returns:
            HTTP response with results of the mutation
        """
        try:
            request_data = await request.json()
            result = do_code_mutator.handle_mutate_request(request_data)
            return result
        except Exception as e:
            logger.error(f"Error handling mutate request: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "code": 500,
            }


def main():
    """Main entry point for the Code Mutator."""
    logger.info("Starting Code Mutator")
    
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="AIDevOS Code Mutator")
    parser.add_argument(
        "--prompt",
        type=str,
        help="Prompt for code mutation",
    )
    parser.add_argument(
        "--file-path",
        type=str,
        help="Path to the file to modify",
    )
    parser.add_argument(
        "--auto-deploy",
        action="store_true",
        help="Automatically deploy the changes",
    )
    parser.add_argument(
        "--repository",
        type=str,
        default="owner/repo",
        help="Repository in the format 'owner/repo'",
    )
    parser.add_argument(
        "--base-branch",
        type=str,
        default="main",
        help="Base branch to branch from",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="Name of the LLM model to use",
    )
    
    args = parser.parse_args()
    
    if args.prompt and args.file_path:
        # Create Code Mutator and run mutation
        code_mutator = CodeMutator(
            repository=args.repository,
            base_branch=args.base_branch,
            model_name=args.model,
        )
        
        result = code_mutator.mutate(
            prompt=args.prompt,
            file_path=args.file_path,
            auto_deploy=args.auto_deploy,
        )
        
        print(json.dumps(result, indent=2))
    else:
        logger.error("No prompt or file path provided")
        parser.print_help()


if __name__ == "__main__":
    main()
