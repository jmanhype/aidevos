#!/usr/bin/env python3
"""
DSPy-enabled Agent implementation for AIDevOS.

This module defines the DSPyAgent class that extends the BaseAgent with
language model capabilities using DSPy.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union, Type

from .base_agent import BaseAgent
from .dspy_modules import (
    PMAgentModule, DevAgentModule, DevOpsAgentModule, UXAgentModule
)

# Configure environment variables for OpenAI
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "your-api-key-here"  # Replace with your actual key or fetch from secure storage


class DSPyAgent(BaseAgent):
    """
    DSPyAgent extends BaseAgent with language model capabilities using DSPy.
    
    This agent uses DSPy modules to process tasks, allowing for more sophisticated
    reasoning and responses powered by language models.
    """
    
    def __init__(
        self, 
        agent_id: str, 
        role: str, 
        capabilities: List[str],
        module_class: Optional[Type] = None
    ):
        """
        Initialize a new DSPyAgent instance.
        
        Args:
            agent_id: Unique identifier for this agent.
            role: The role this agent fulfills (e.g., "PM", "Dev", "DevOps", "UX").
            capabilities: List of capabilities this agent has.
            module_class: The DSPy module class to use for this agent.
        """
        super().__init__(agent_id, role, capabilities)
        self.logger = logging.getLogger(f"aidevos.dspy_agent.{agent_id}")
        self.logger.setLevel(logging.INFO)
        
        # Initialize the appropriate DSPy module based on role
        if module_class:
            self.module = module_class()
        else:
            if role == "PM":
                self.module = PMAgentModule()
            elif role == "Dev":
                self.module = DevAgentModule()
            elif role == "DevOps":
                self.module = DevOpsAgentModule()
            elif role == "UX":
                self.module = UXAgentModule()
            else:
                self.logger.warning(f"No specific DSPy module for role: {role}. Using generic handling.")
                self.module = None
                
        self.logger.info(f"Initialized DSPy-enabled {role} Agent: {agent_id}")
        
    async def process_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a task using DSPy modules for more sophisticated responses.
        
        Args:
            task: The task to process.
            
        Returns:
            The response to the task, or None if no response is needed.
        """
        self.logger.info(f"Processing task with DSPy: {task.get('type', 'unknown')}")
        
        # Extract required information
        task_type = task.get("type", "")
        content = task.get("content", {})
        
        # Collect context information
        context = {
            "agent_state": self.state,
            "agent_capabilities": self.capabilities,
            "timestamp": task.get("timestamp")
        }
        
        # Skip processing if no module is available
        if self.module is None:
            self.logger.warning("No DSPy module available, falling back to base implementation")
            return await super().process_task(task)
        
        try:
            # Process the task with the DSPy module
            result = self.module(
                agent_id=self.agent_id,
                agent_role=self.role,
                task=task,
                context=context
            )
            
            self.logger.info(f"DSPy module processed task successfully")
            
            # If this task was sent by another agent, send a response back
            if "sender" in task:
                return await self.send_message(
                    recipient=task["sender"],
                    content=result,
                    message_type="response",
                    reply_to=task.get("message_id")
                )
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Error processing task with DSPy: {e}", exc_info=True)
            
            # Fall back to the base implementation if DSPy processing fails
            self.logger.info("Falling back to base implementation")
            return await super().process_task(task)
            
    async def send_message(
        self, 
        recipient: str, 
        content: Dict[str, Any], 
        message_type: str = "task", 
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to another agent.
        
        Args:
            recipient: ID of the agent to send the message to.
            content: Content of the message.
            message_type: Type of message (task, response, etc.).
            reply_to: ID of the message this is a reply to, if applicable.
            
        Returns:
            The sent message.
        """
        # Enhance the sent message with more context if we're using a language model
        if isinstance(content, dict) and not content.get("enhanced_by_dspy"):
            content["enhanced_by_dspy"] = True
            content["generated_by"] = f"{self.role} Agent ({self.agent_id})"
            
        return await super().send_message(recipient, content, message_type, reply_to)


class DSPyPMAgent(DSPyAgent):
    """DSPy-enabled Project Management Agent."""
    
    def __init__(self, agent_id: str):
        """
        Initialize a new DSPyPMAgent.
        
        Args:
            agent_id: Unique identifier for this agent.
        """
        capabilities = [
            "requirements_analysis",
            "architecture_design",
            "feature_planning",
            "progress_tracking",
            "release_management"
        ]
        super().__init__(agent_id, "PM", capabilities, PMAgentModule)


class DSPyDevAgent(DSPyAgent):
    """DSPy-enabled Development Agent."""
    
    def __init__(self, agent_id: str):
        """
        Initialize a new DSPyDevAgent.
        
        Args:
            agent_id: Unique identifier for this agent.
        """
        capabilities = [
            "code_implementation",
            "code_review",
            "technical_specification",
            "architecture_review",
            "performance_optimization"
        ]
        super().__init__(agent_id, "Dev", capabilities, DevAgentModule)


class DSPyDevOpsAgent(DSPyAgent):
    """DSPy-enabled DevOps Agent."""
    
    def __init__(self, agent_id: str):
        """
        Initialize a new DSPyDevOpsAgent.
        
        Args:
            agent_id: Unique identifier for this agent.
        """
        capabilities = [
            "deployment",
            "infrastructure_management",
            "ci_cd_pipeline",
            "monitoring",
            "security_assessment",
            "scalability_planning"
        ]
        super().__init__(agent_id, "DevOps", capabilities, DevOpsAgentModule)


class DSPyUXAgent(DSPyAgent):
    """DSPy-enabled UX Agent."""
    
    def __init__(self, agent_id: str):
        """
        Initialize a new DSPyUXAgent.
        
        Args:
            agent_id: Unique identifier for this agent.
        """
        capabilities = [
            "ui_design",
            "interface_mockups",
            "usability_testing",
            "design_system_maintenance",
            "architecture_review",
            "user_flow_design",
            "style_guide_creation"
        ]
        super().__init__(agent_id, "UX", capabilities, UXAgentModule)
