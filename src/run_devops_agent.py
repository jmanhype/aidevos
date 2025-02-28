#!/usr/bin/env python
"""
DevOps & QA Agent Execution Script.

This script runs the DevOps & QA agent, which is responsible for CI/CD pipeline,
testing, deployment, and monitoring tasks in the AIDevOS system.
"""

import argparse
import logging
import os
import sys
import time
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.devops_agent")


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="AIDevOS DevOps & QA Agent")
    
    # Command options
    parser.add_argument(
        "--task",
        type=str,
        choices=["deploy", "test", "monitor", "improve", "ci", "cd", "all"],
        default="all",
        help="Task to perform",
    )
    
    # Environment options
    parser.add_argument(
        "--environment",
        type=str,
        choices=["dev", "staging", "production"],
        default="dev",
        help="Target environment",
    )
    
    # Component options
    parser.add_argument(
        "--component",
        type=str,
        help="Specific component to work with",
    )
    
    # Configuration options
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    
    # Output options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output",
    )
    
    return parser.parse_args()


def run_deployment(args: argparse.Namespace) -> bool:
    """
    Run deployment tasks.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if deployment was successful, False otherwise
    """
    logger.info(f"Running deployment to {args.environment} environment")
    
    try:
        from src.deployment.deploy import DeploymentManager, DeploymentEnvironment, DeploymentStrategy
        
        # Create deployment manager
        manager = DeploymentManager(
            environment=DeploymentEnvironment(args.environment),
            strategy=DeploymentStrategy.BLUE_GREEN,
            config_path=args.config,
        )
        
        # Deploy
        if manager.deploy():
            logger.info("Deployment completed successfully")
            return True
        else:
            logger.error("Deployment failed")
            return False
    
    except Exception as e:
        logger.error(f"Error during deployment: {str(e)}")
        return False


def run_tests(args: argparse.Namespace) -> bool:
    """
    Run tests.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if tests passed, False otherwise
    """
    logger.info(f"Running tests in {args.environment} environment")
    
    try:
        from src.testing.run_tests import main as run_tests_main
        
        # Set up test arguments
        test_args = ["--environment", args.environment]
        
        if args.component:
            test_args.extend(["--component", args.component])
        
        if args.verbose:
            test_args.append("--verbose")
        
        if args.quiet:
            test_args.append("--quiet")
        
        # Run tests
        sys.argv = [sys.argv[0]] + test_args
        result = run_tests_main()
        
        # Check result
        if result == 0:
            logger.info("Tests passed")
            return True
        else:
            logger.error("Tests failed")
            return False
    
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        return False


def run_monitoring(args: argparse.Namespace) -> bool:
    """
    Run monitoring tasks.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if monitoring was set up successfully, False otherwise
    """
    logger.info(f"Running monitoring for {args.environment} environment")
    
    try:
        from src.monitoring.setup import MonitoringSetup, MonitoringEnvironment, MonitoringComponent
        
        # Create monitoring setup
        setup = MonitoringSetup(
            environment=MonitoringEnvironment(args.environment),
            config_dir=os.path.dirname(args.config) if args.config else "config/monitoring",
            output_dir=f"deployment/monitoring/{args.environment}",
        )
        
        # Set up monitoring
        if args.component:
            component = MonitoringComponent(args.component)
            success = setup.setup_component(component)
        else:
            success = setup.setup_monitoring_stack()
        
        if success:
            logger.info("Monitoring setup completed successfully")
            return True
        else:
            logger.error("Monitoring setup failed")
            return False
    
    except Exception as e:
        logger.error(f"Error during monitoring setup: {str(e)}")
        return False


def run_improvement(args: argparse.Namespace) -> bool:
    """
    Run self-improvement tasks.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if improvement tasks completed successfully, False otherwise
    """
    logger.info("Running self-improvement analysis")
    
    try:
        from src.deployment.self_improvement import SelfImprovementEngine
        
        # Create self-improvement engine
        engine = SelfImprovementEngine(
            config_path=args.config or "config/self_improvement.json",
        )
        
        # Analyze system
        optimizations = engine.analyze_system()
        
        # Print optimizations
        if optimizations:
            logger.info(f"Found {len(optimizations)} potential optimizations:")
            for opt in optimizations:
                logger.info(f"- [{opt['priority'].upper()}] {opt['description']}")
        else:
            logger.info("No optimizations found")
        
        # Apply automatic optimizations
        applied_count = engine.apply_automatic_optimizations()
        logger.info(f"Applied {applied_count} automatic optimizations")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during self-improvement analysis: {str(e)}")
        return False


def run_ci(args: argparse.Namespace) -> bool:
    """
    Run CI tasks.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if CI tasks completed successfully, False otherwise
    """
    logger.info("Running CI tasks")
    
    try:
        from src.deployment.ci_cd.github_actions import generate_default_workflows
        
        # Generate GitHub Actions workflows
        generate_default_workflows()
        
        # Run tests
        if not run_tests(args):
            return False
        
        logger.info("CI tasks completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during CI tasks: {str(e)}")
        return False


def run_cd(args: argparse.Namespace) -> bool:
    """
    Run CD tasks.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if CD tasks completed successfully, False otherwise
    """
    logger.info("Running CD tasks")
    
    try:
        # Run deployment
        if not run_deployment(args):
            return False
        
        # Set up monitoring
        if not run_monitoring(args):
            return False
        
        logger.info("CD tasks completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during CD tasks: {str(e)}")
        return False


def run_all_tasks(args: argparse.Namespace) -> bool:
    """
    Run all DevOps & QA tasks.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if all tasks completed successfully, False otherwise
    """
    logger.info("Running all DevOps & QA tasks")
    
    results = []
    
    # Run CI
    results.append(run_ci(args))
    
    # Run CD
    results.append(run_cd(args))
    
    # Run improvement
    results.append(run_improvement(args))
    
    # Check results
    return all(results)


def main() -> int:
    """
    Main entry point for the DevOps & QA agent.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    logger.info("Starting AIDevOS DevOps & QA Agent")
    start_time = time.time()
    
    success = False
    
    # Run requested task
    if args.task == "deploy":
        success = run_deployment(args)
    elif args.task == "test":
        success = run_tests(args)
    elif args.task == "monitor":
        success = run_monitoring(args)
    elif args.task == "improve":
        success = run_improvement(args)
    elif args.task == "ci":
        success = run_ci(args)
    elif args.task == "cd":
        success = run_cd(args)
    elif args.task == "all":
        success = run_all_tasks(args)
    
    # Log summary
    duration = time.time() - start_time
    logger.info(f"DevOps & QA Agent completed in {duration:.2f} seconds")
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())