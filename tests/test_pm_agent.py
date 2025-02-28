"""
Tests for the PM Agent implementation.
"""

import asyncio
import json
import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.pm_agent import PMAgent


class TestPMAgent(unittest.TestCase):
    """Test cases for the PM Agent."""
    
    def setUp(self):
        """Set up the test environment."""
        self.pm_agent = PMAgent("test_pm_agent")
    
    def test_initialization(self):
        """Test that the PM Agent initializes correctly."""
        self.assertEqual(self.pm_agent.agent_id, "test_pm_agent")
        self.assertEqual(self.pm_agent.role, "PM")
        self.assertIn("architecture_design", self.pm_agent.capabilities)
        self.assertIn("feature_planning", self.pm_agent.capabilities)
        self.assertIn("task_assignment", self.pm_agent.capabilities)
        
        # Check that the state was initialized correctly
        self.assertEqual(self.pm_agent.state["current_features"], [])
        self.assertEqual(self.pm_agent.state["assigned_tasks"], {})
        self.assertEqual(self.pm_agent.state["architecture_decisions"], [])
    
    def test_get_current_roadmap(self):
        """Test the get_current_roadmap method."""
        # Add some test features
        self.pm_agent.state["current_features"] = [
            {"name": "Feature 1", "priority": "medium"},
            {"name": "Feature 2", "priority": "high"},
            {"name": "Feature 3", "priority": "low"}
        ]
        
        # Get the roadmap and check that it's sorted by priority
        roadmap = self.pm_agent.get_current_roadmap()
        self.assertEqual(roadmap[0]["name"], "Feature 2")  # High priority
        self.assertEqual(roadmap[1]["name"], "Feature 1")  # Medium priority
        self.assertEqual(roadmap[2]["name"], "Feature 3")  # Low priority
    
    def test_get_architecture_decisions(self):
        """Test the get_architecture_decisions method."""
        # Add some test decisions
        test_decisions = [
            {"id": "ADR-1", "title": "Decision 1"},
            {"id": "ADR-2", "title": "Decision 2"}
        ]
        self.pm_agent.state["architecture_decisions"] = test_decisions
        
        # Get the decisions and check that they match
        decisions = self.pm_agent.get_architecture_decisions()
        self.assertEqual(len(decisions), 2)
        self.assertEqual(decisions[0]["id"], "ADR-1")
        self.assertEqual(decisions[1]["id"], "ADR-2")
    
    def test_process_task_unknown_type(self):
        """Test that the agent handles unknown task types."""
        # We need to use asyncio to run the coroutine
        loop = asyncio.get_event_loop()
        
        # Create a test task with an unknown type
        task = {
            "message_id": "test_message_id",
            "sender": "test_sender",
            "recipient": "test_pm_agent",
            "timestamp": "2025-03-01T12:00:00Z",
            "message_type": "task",
            "content": {
                "task_type": "unknown_task_type",
                "data": "Some test data"
            }
        }
        
        # Process the task and check the response
        result = loop.run_until_complete(self.pm_agent.process_task(task))
        
        # Verify that we got a response of the right type
        self.assertEqual(result["type"], "message")
        payload = result["payload"]
        self.assertEqual(payload["message_type"], "response")
        self.assertEqual(payload["recipient"], "test_sender")
        self.assertEqual(payload["reply_to"], "test_message_id")
        
        # Verify that the response indicates we don't know how to handle this task
        self.assertEqual(payload["content"]["status"], "acknowledged")
        self.assertIn("received the task but has no specific implementation", 
                      payload["content"]["message"])


if __name__ == "__main__":
    unittest.main()