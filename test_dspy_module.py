#!/usr/bin/env python3
"""
Test script for DSPy modules in AIDevOS.

This script provides a way to test individual DSPy agent modules
to verify they're working correctly.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("aidevos.dspy_test")

# Add src directory to path
sys.path.insert(0, os.path.abspath('.'))

# Import DSPy modules
from src.agents.dspy_modules import PMAgentModule, DevAgentModule, DevOpsAgentModule, UXAgentModule
from src.config.dspy_config import DSPyConfig

# Initialize DSPy
dspy_config = DSPyConfig()

async def test_pm_agent() -> None:
    """Test the PM Agent module functionality."""
    logger.info("Testing PM Agent Module")
    
    # Create a PM Agent module
    pm_module = PMAgentModule()
    
    # Create a test task for requirements analysis
    task = {
        "type": "requirements_analysis",
        "description": """
        Create a notification system for the AIDevOS platform that can:
        1. Send notifications to users via email, SMS, and in-app channels
        2. Allow users to configure notification preferences
        3. Support templating for notification content
        4. Track delivery status and provide retry mechanisms
        5. Scale to handle thousands of notifications per minute
        """
    }
    
    # Create some context
    context = {
        "agent_state": {},
        "agent_capabilities": ["requirements_analysis", "architecture_design"],
        "timestamp": "2025-02-28T02:28:00"
    }
    
    # Process the task
    logger.info("Processing requirements analysis task")
    result = pm_module(
        agent_id="test_pm_agent",
        agent_role="PM",
        task=task, 
        context=context
    )
    
    # Print the results
    logger.info("Requirements Analysis Results:")
    print(json.dumps(result, indent=2))
    
    return result

async def test_dev_agent() -> None:
    """Test the Dev Agent module functionality."""
    logger.info("Testing Dev Agent Module")
    
    # Create a Dev Agent module
    dev_module = DevAgentModule()
    
    # Create a test task for implementation
    task = {
        "type": "service_implementation",
        "service_name": "NotificationService",
        "architecture": {
            "components": [
                {
                    "name": "NotificationService",
                    "description": "Core service for managing notifications",
                    "interfaces": ["REST API", "Message Queue"]
                }
            ]
        },
        "requirements": {
            "functional": [
                "Send notifications via multiple channels",
                "Track delivery status",
                "Support templated notifications"
            ]
        }
    }
    
    # Create some context
    context = {
        "agent_state": {},
        "agent_capabilities": ["code_implementation", "code_review"],
        "timestamp": "2025-02-28T02:28:00"
    }
    
    # Process the task
    logger.info("Processing service implementation task")
    result = dev_module(
        agent_id="test_dev_agent",
        agent_role="Dev",
        task=task, 
        context=context
    )
    
    # Print the results
    logger.info("Service Implementation Results:")
    print(json.dumps(result, indent=2))
    
    return result

async def main() -> None:
    """Run the test script."""
    logger.info("Starting DSPy module tests")
    
    # Ensure the API key is set
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        logger.error("No OpenAI API key found in environment variables")
        print("Please set your OpenAI API key in the environment:")
        print('export OPENAI_API_KEY="your-key-here"')
        return
    
    # Select which test to run based on command line argument
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "pm":
            await test_pm_agent()
        elif test_type == "dev":
            await test_dev_agent()
        else:
            logger.error(f"Unknown test type: {test_type}")
            print("Available test types: pm, dev")
    else:
        # Run all tests if no argument provided
        await test_pm_agent()
        await test_dev_agent()
    
    logger.info("Tests completed")

if __name__ == "__main__":
    asyncio.run(main())
