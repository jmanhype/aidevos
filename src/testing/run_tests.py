#!/usr/bin/env python
"""
Test Runner Script for AIDevOS.

This script provides a command-line interface for running AIDevOS tests,
with options for selecting test levels, environments, and patterns.
"""

import argparse
import logging
import sys
import os
import time
from pathlib import Path
from typing import List, Optional

from src.testing.framework import TestLevel, TestEnvironment, run_tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.testing.runner")


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="AIDevOS Test Runner")
    
    parser.add_argument(
        "--test-path",
        type=str,
        default="tests",
        help="Path to the tests to run",
    )
    
    parser.add_argument(
        "--level",
        type=str,
        choices=[level.value for level in TestLevel],
        help="Test level to run",
    )
    
    parser.add_argument(
        "--environment",
        type=str,
        choices=[env.value for env in TestEnvironment],
        help="Test environment to use",
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        default="test_*.py",
        help="Pattern for test files",
    )
    
    parser.add_argument(
        "--component",
        type=str,
        help="Component to test (e.g., 'orchestration', 'deployment')",
    )
    
    parser.add_argument(
        "--xml-report",
        action="store_true",
        help="Generate XML report",
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report",
    )
    
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


def build_test_command(args: argparse.Namespace) -> List[str]:
    """
    Build the pytest command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        List of command-line arguments for pytest
    """
    command = ["-v"] if args.verbose else []
    
    # Add test path
    test_path = args.test_path
    if args.component:
        test_path = os.path.join(test_path, f"test_{args.component}.py")
    command.append(test_path)
    
    # Add pattern
    if args.pattern:
        command.append(f"--pattern={args.pattern}")
    
    # Add level
    if args.level:
        command.append(f"-k={args.level}")
    
    # Add XML report
    if args.xml_report:
        command.append("--junitxml=test-results.xml")
    
    # Add coverage
    if args.coverage:
        command.append("--cov=src")
        command.append("--cov-report=xml")
        command.append("--cov-report=term")
    
    return command


def main() -> int:
    """
    Main entry point for the test runner script.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    # Set environment variable for test environment
    if args.environment:
        os.environ["AIDEVOS_TEST_ENV"] = args.environment
    
    # Set log level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting AIDevOS test run")
    start_time = time.time()
    
    # Build pytest command
    command = build_test_command(args)
    logger.info(f"Running tests with command: pytest {' '.join(command)}")
    
    # Run tests
    import pytest
    result = pytest.main(command)
    
    # Log summary
    duration = time.time() - start_time
    logger.info(f"Test run completed in {duration:.2f} seconds")
    
    # Return appropriate exit code
    return result


if __name__ == "__main__":
    sys.exit(main())