#!/usr/bin/env python3
"""
AIDevOS Agent Runner

This script initializes and runs the AIDevOS agent system for development and testing.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('aidevos')

# Import our agent implementations
from agents.base_agent import BaseAgent
from agents.pm_agent import PMAgent


async def demo_communication():
    """Demonstrate basic agent communication."""
    # Create our agents
    pm_agent = PMAgent(f"pm_{uuid.uuid4().hex[:8]}")
    logger.info(f"Created PM Agent: {pm_agent}")
    
    # Start the PM agent
    logger.info("Starting PM Agent...")
    pm_task = asyncio.create_task(pm_agent.start())
    
    # Wait a moment for the agent to start
    await asyncio.sleep(1)
    
    # Create a feature planning task
    feature_task = {
        "message_id": f"task_{uuid.uuid4().hex}",
        "sender": "user",
        "recipient": pm_agent.agent_id,
        "timestamp": datetime.utcnow().isoformat(),
        "message_type": "task",
        "content": {
            "task_type": "feature_planning",
            "feature_name": "Basic Agent Framework",
            "feature_description": "Implement the core agent abstractions and communication protocol",
            "priority": "high"
        }
    }
    
    # Send the task to the PM agent
    logger.info(f"Sending feature planning task to PM Agent: {feature_task['content']['feature_name']}")
    await pm_agent.receive_message(feature_task)
    
    # Wait a moment for the task to be processed
    await asyncio.sleep(1)
    
    # Create an architecture decision task
    adr_task = {
        "message_id": f"task_{uuid.uuid4().hex}",
        "sender": "user",
        "recipient": pm_agent.agent_id,
        "timestamp": datetime.utcnow().isoformat(),
        "message_type": "task",
        "content": {
            "task_type": "architecture_decision",
            "title": "Agent Communication Protocol",
            "context": "Agents need to communicate efficiently while maintaining a clear record of interactions.",
            "decision": "Implement a structured JSON-based message protocol with required fields.",
            "consequences": "All agent communication will be structured and traceable.",
            "status": "accepted"
        }
    }
    
    # Send the task to the PM agent
    logger.info(f"Sending architecture decision task to PM Agent: {adr_task['content']['title']}")
    await pm_agent.receive_message(adr_task)
    
    # Wait a moment for the task to be processed
    await asyncio.sleep(1)
    
    # Get the current roadmap
    roadmap = pm_agent.get_current_roadmap()
    logger.info(f"Current roadmap: {json.dumps(roadmap, indent=2)}")
    
    # Get the architecture decisions
    decisions = pm_agent.get_architecture_decisions()
    logger.info(f"Architecture decisions: {json.dumps(decisions, indent=2)}")
    
    # Stop the PM agent
    logger.info("Stopping PM Agent...")
    pm_agent.running = False
    await pm_task


async def main():
    """Main entry point for the agent runner."""
    logger.info("Starting AIDevOS Agent System")
    
    # Run our demo
    await demo_communication()
    
    logger.info("AIDevOS Agent System completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
        sys.exit(0)