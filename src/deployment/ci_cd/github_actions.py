"""
GitHub Actions CI/CD Pipeline Generator for AIDevOS.

This module provides utilities to dynamically generate, manage and optimize
GitHub Actions workflows for the AIDevOS CI/CD pipeline.
"""

import os
import yaml
from typing import Dict, List, Optional, Union, Any
from pathlib import Path


class GitHubActionsGenerator:
    """Generator for GitHub Actions workflow files."""

    def __init__(self, output_dir: str = ".github/workflows"):
        """
        Initialize the GitHub Actions workflow generator.
        
        Args:
            output_dir: Directory where workflow files will be saved
        """
        self.output_dir = output_dir
        
    def generate_workflow_file(self, workflow_config: Dict[str, Any], filename: str) -> str:
        """
        Generate a GitHub Actions workflow file from a configuration dictionary.
        
        Args:
            workflow_config: Dictionary containing the workflow configuration
            filename: Name of the workflow file (without extension)
            
        Returns:
            Path to the generated workflow file
        """
        os.makedirs(self.output_dir, exist_ok=True)
        file_path = os.path.join(self.output_dir, f"{filename}.yml")
        
        with open(file_path, 'w') as f:
            yaml.dump(workflow_config, f, sort_keys=False)
            
        return file_path

    def create_ci_workflow(self, 
                          name: str = "AIDevOS CI Pipeline",
                          python_versions: List[str] = ["3.8", "3.9", "3.10"],
                          os_list: List[str] = ["ubuntu-latest"]) -> Dict[str, Any]:
        """
        Create a CI workflow configuration for AIDevOS.
        
        Args:
            name: Name of the workflow
            python_versions: List of Python versions to test against
            os_list: List of operating systems to test on
            
        Returns:
            Dictionary containing the CI workflow configuration
        """
        workflow = {
            "name": name,
            "on": {
                "push": {
                    "branches": ["main", "dev", "feature/**", "bugfix/**"]
                },
                "pull_request": {
                    "branches": ["main", "dev"]
                }
            },
            "jobs": {
                "lint": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.10"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Lint with ruff",
                            "run": "ruff check ."
                        },
                        {
                            "name": "Type check with mypy",
                            "run": "mypy src"
                        }
                    ]
                },
                "test": {
                    "needs": "lint",
                    "runs-on": "${{ matrix.os }}",
                    "strategy": {
                        "matrix": {
                            "os": os_list,
                            "python-version": python_versions
                        }
                    },
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Set up Python ${{ matrix.python-version }}",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "${{ matrix.python-version }}"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run tests",
                            "run": "pytest tests/ --cov=src --cov-report=xml"
                        },
                        {
                            "name": "Upload coverage to Codecov",
                            "uses": "codecov/codecov-action@v3",
                            "with": {"file": "./coverage.xml"}
                        }
                    ]
                },
                "security-scan": {
                    "needs": "lint",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.10"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt bandit safety"
                        },
                        {
                            "name": "Run Bandit security scan",
                            "run": "bandit -r src/ -f json -o bandit-results.json || true"
                        },
                        {
                            "name": "Check for vulnerable dependencies",
                            "run": "safety check"
                        }
                    ]
                }
            }
        }
        
        return workflow
    
    def create_cd_workflow(self, 
                           name: str = "AIDevOS CD Pipeline",
                           environments: List[str] = ["dev", "staging", "production"]) -> Dict[str, Any]:
        """
        Create a CD workflow configuration for AIDevOS.
        
        Args:
            name: Name of the workflow
            environments: List of deployment environments
            
        Returns:
            Dictionary containing the CD workflow configuration
        """
        workflow = {
            "name": name,
            "on": {
                "push": {
                    "branches": ["main"]
                },
                "workflow_dispatch": {
                    "inputs": {
                        "environment": {
                            "description": "Environment to deploy to",
                            "required": True,
                            "default": "dev",
                            "type": "choice",
                            "options": environments
                        }
                    }
                }
            },
            "jobs": {}
        }
        
        # Add deployment jobs for each environment with sequential dependencies
        prev_env = None
        for env in environments:
            workflow["jobs"][f"deploy-{env}"] = {
                "runs-on": "ubuntu-latest",
                "environment": env,
                # Make each deployment dependent on the previous one succeeding
                **({"needs": f"deploy-{prev_env}"} if prev_env else {}),
                "steps": [
                    {"uses": "actions/checkout@v3"},
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "3.10"}
                    },
                    {
                        "name": "Install dependencies",
                        "run": "pip install -r requirements.txt"
                    },
                    {
                        "name": "Deploy to {env}".format(env=env),
                        "run": f"python src/deployment/deploy.py --environment {env}"
                    },
                    {
                        "name": "Run smoke tests",
                        "run": f"python src/testing/smoke_tests.py --environment {env}"
                    },
                    {
                        "name": "Setup monitoring",
                        "run": f"python src/monitoring/setup.py --environment {env}"
                    }
                ]
            }
            prev_env = env
        
        return workflow
        
    def create_durable_objects_workflow(self, name: str = "Durable Objects CI/CD") -> Dict[str, Any]:
        """
        Create a workflow specifically for Durable Objects CI/CD.
        
        Args:
            name: Name of the workflow
            
        Returns:
            Dictionary containing the DO workflow configuration
        """
        workflow = {
            "name": name,
            "on": {
                "push": {
                    "paths": ["src/orchestration/**"]
                },
                "pull_request": {
                    "paths": ["src/orchestration/**"]
                },
                "workflow_dispatch": {}
            },
            "jobs": {
                "build-test-deploy": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.10"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run Durable Objects tests",
                            "run": "pytest tests/orchestration/ -v"
                        },
                        {
                            "name": "Build Durable Objects",
                            "run": "python src/deployment/do_builder.py"
                        },
                        {
                            "name": "Deploy Durable Objects",
                            "if": "github.ref == 'refs/heads/main'",
                            "run": "python src/deployment/do_deployer.py"
                        }
                    ]
                }
            }
        }
        
        return workflow


def generate_default_workflows():
    """Generate the default set of GitHub Actions workflows for AIDevOS."""
    generator = GitHubActionsGenerator()
    
    # Generate CI workflow
    ci_config = generator.create_ci_workflow()
    generator.generate_workflow_file(ci_config, "ci")
    
    # Generate CD workflow
    cd_config = generator.create_cd_workflow()
    generator.generate_workflow_file(cd_config, "cd")
    
    # Generate Durable Objects workflow
    do_config = generator.create_durable_objects_workflow()
    generator.generate_workflow_file(do_config, "durable_objects")
    
    print("Generated GitHub Actions workflow files in .github/workflows/")


if __name__ == "__main__":
    generate_default_workflows()