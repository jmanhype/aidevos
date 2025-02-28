#!/usr/bin/env python3
"""
Example of a self-modifying agent using DSPy and the Code Mutator.

This example shows how to create an agent that can modify its own code
based on performance metrics and user feedback.
"""

import logging
import time
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dspy
from dspy.teleprompt import BootstrapFewShot

from src.agents.dspy_agent import DSPyAgent, DSPyDevAgent
from src.config.dspy_config import DSPyConfig
from src.deployment.code_mutator import CodeMutator
from src.deployment.self_improvement import SelfImprovementEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.self_modifying_agent")


class SelfModificationSignature(dspy.Signature):
    """
    Signature for generating self-modification prompts based on performance metrics.
    """
    
    performance_metrics = dspy.InputField(desc="Performance metrics from the agent")
    current_code_path = dspy.InputField(desc="Path to the current code implementation")
    improvement_goal = dspy.InputField(desc="What aspect of the code needs improvement")
    
    modification_prompt = dspy.OutputField(desc="A prompt for the code mutator to make specific improvements")
    expected_benefits = dspy.OutputField(desc="Expected benefits from the proposed changes")


class SelfModifyingAgent(DSPyDevAgent):
    """
    A self-modifying agent that can improve its own code based on performance metrics.
    """
    
    def __init__(
        self,
        name: str = "SelfImproving",
        model_name: str = "gpt-4",
        github_token: Optional[str] = None,
        repository: str = "owner/repo",
        base_branch: str = "main",
    ):
        """
        Initialize the self-modifying agent.
        
        Args:
            name: Name of the agent
            model_name: Name of the LLM model to use
            github_token: GitHub personal access token
            repository: Repository in the format "owner/repo"
            base_branch: Base branch to branch from
        """
        super().__init__(name=name, model_name=model_name)
        
        # Initialize the self-improvement engine
        self.improvement_engine = SelfImprovementEngine()
        
        # Initialize the code mutator
        self.code_mutator = CodeMutator(
            github_token=github_token,
            repository=repository,
            base_branch=base_branch,
            model_name=model_name,
        )
        
        # Initialize the self-modification module
        self.self_modification = dspy.ChainOfThought(SelfModificationSignature)
        
        logger.info(f"Self-modifying agent {name} initialized")
    
    def collect_performance_metrics(self) -> Dict[str, Any]:
        """
        Collect performance metrics for the agent.
        
        Returns:
            Dictionary with performance metrics
        """
        # This is a simple example that would be expanded in a real implementation
        metrics = {
            "response_time": {
                "avg_ms": 1500,
                "p95_ms": 2200,
                "p99_ms": 3500,
            },
            "successful_tasks": 85,
            "failed_tasks": 15,
            "success_rate": 0.85,
            "memory_usage_mb": 256,
            "tokens_consumed": 15000,
            "cost_usd": 0.45,
            "user_feedback": {
                "positive": 75,
                "negative": 25,
                "common_complaints": [
                    "Response time too slow",
                    "Missing context from previous interactions",
                ]
            }
        }
        
        return metrics
    
    def analyze_for_improvements(self) -> List[Dict[str, Any]]:
        """
        Analyze the agent's performance and identify improvement opportunities.
        
        Returns:
            List of improvement opportunities
        """
        # Use the improvement engine to analyze system performance
        return self.improvement_engine.analyze_system()
    
    def generate_self_improvement_prompts(self, improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate prompts for self-improvement based on identified opportunities.
        
        Args:
            improvements: List of improvement opportunities
            
        Returns:
            List of mutation requests
        """
        mutation_requests = []
        
        for improvement in improvements:
            try:
                # Get the relevant file path for this improvement
                # In a real implementation, this would be determined based on the improvement type
                file_path = self._determine_file_path_for_improvement(improvement)
                
                # Generate a modification prompt
                result = self.self_modification(
                    performance_metrics=json.dumps(self.collect_performance_metrics()),
                    current_code_path=file_path,
                    improvement_goal=improvement["description"],
                )
                
                mutation_requests.append({
                    "improvement_id": improvement["id"],
                    "prompt": result.modification_prompt,
                    "file_path": file_path,
                    "expected_benefits": result.expected_benefits,
                })
            except Exception as e:
                logger.error(f"Error generating mutation request for improvement {improvement['id']}: {str(e)}")
        
        return mutation_requests
    
    def _determine_file_path_for_improvement(self, improvement: Dict[str, Any]) -> str:
        """
        Determine the file path to modify for a given improvement.
        
        Args:
            improvement: Improvement opportunity
            
        Returns:
            Path to the file to modify
        """
        # This is a simple example that would be expanded in a real implementation
        improvement_type = improvement.get("type", "")
        
        # Map improvement types to file paths
        type_to_path = {
            "performance": __file__,  # Example: improve this file
            "memory": os.path.join(os.path.dirname(__file__), "..", "src", "agents", "dspy_agent.py"),
            "reliability": os.path.join(os.path.dirname(__file__), "..", "src", "deployment", "self_improvement.py"),
        }
        
        return type_to_path.get(improvement_type, __file__)
    
    def self_modify(self, auto_deploy: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze performance, generate improvement prompts, and apply modifications.
        
        Args:
            auto_deploy: Whether to automatically deploy the changes
            
        Returns:
            List of mutation results
        """
        logger.info("Starting self-modification process")
        
        # Analyze performance and identify improvement opportunities
        improvements = self.analyze_for_improvements()
        logger.info(f"Identified {len(improvements)} improvement opportunities")
        
        if not improvements:
            logger.info("No improvements found, nothing to modify")
            return []
        
        # Generate mutation requests
        mutation_requests = self.generate_self_improvement_prompts(improvements)
        logger.info(f"Generated {len(mutation_requests)} mutation requests")
        
        # Apply mutations
        mutation_results = []
        for request in mutation_requests:
            try:
                logger.info(f"Applying mutation for improvement {request['improvement_id']}")
                
                # Mutate the code
                result = self.code_mutator.mutate(
                    prompt=request["prompt"],
                    file_path=request["file_path"],
                    auto_deploy=auto_deploy,
                )
                
                # Mark the improvement as applied
                if result["status"] == "success":
                    self.improvement_engine.apply_optimization(request["improvement_id"])
                
                mutation_results.append({
                    "improvement_id": request["improvement_id"],
                    "mutation_result": result,
                })
            except Exception as e:
                logger.error(f"Error applying mutation for improvement {request['improvement_id']}: {str(e)}")
                mutation_results.append({
                    "improvement_id": request["improvement_id"],
                    "status": "error",
                    "error": str(e),
                })
        
        return mutation_results


def main():
    """Main entry point for the self-modifying agent example."""
    logger.info("Starting self-modifying agent example")
    
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="AIDevOS Self-Modifying Agent Example")
    parser.add_argument(
        "--auto-deploy",
        action="store_true",
        help="Automatically deploy the changes",
    )
    parser.add_argument(
        "--repository",
        type=str,
        default=os.environ.get("GITHUB_REPOSITORY", "owner/repo"),
        help="Repository in the format 'owner/repo'",
    )
    parser.add_argument(
        "--base-branch",
        type=str,
        default=os.environ.get("GITHUB_BASE_BRANCH", "main"),
        help="Base branch to branch from",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.environ.get("AIDEVOS_MODEL", "gpt-4"),
        help="Name of the LLM model to use",
    )
    
    args = parser.parse_args()
    
    # Initialize the self-modifying agent
    agent = SelfModifyingAgent(
        model_name=args.model,
        github_token=os.environ.get("GITHUB_TOKEN"),
        repository=args.repository,
        base_branch=args.base_branch,
    )
    
    # Run the self-modification process
    results = agent.self_modify(auto_deploy=args.auto_deploy)
    
    # Print the results
    print("\nSelf-Modification Results:")
    for result in results:
        improvement_id = result.get("improvement_id", "unknown")
        status = result.get("status", result.get("mutation_result", {}).get("status", "unknown"))
        
        print(f"\nImprovement ID: {improvement_id}")
        print(f"Status: {status}")
        
        if status == "error":
            print(f"Error: {result.get('error', result.get('mutation_result', {}).get('error', 'unknown'))}")
        elif status == "success":
            mutation_result = result.get("mutation_result", {})
            print(f"File Path: {mutation_result.get('file_path', 'unknown')}")
            print(f"Deployed: {mutation_result.get('deployed', False)}")
            if mutation_result.get("deployed", False):
                print(f"PR URL: {mutation_result.get('pr_url', 'unknown')}")
            print("\nExplanation:")
            print(mutation_result.get("explanation", "No explanation provided"))
    
    print("\nSelf-modification process completed")


if __name__ == "__main__":
    main()
