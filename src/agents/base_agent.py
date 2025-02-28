"""
Base Agent implementation for AIDevOS.

This module defines the core BaseAgent class that all specialized agents inherit from,
providing common functionality for communication, state management, and task processing.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


class BaseAgent:
    """
    BaseAgent serves as the foundation for all specialized agents in AIDevOS.
    
    It provides core functionality for communication, state management, and task processing
    that is common across all agent types.
    """
    
    def __init__(self, agent_id: str, role: str, capabilities: List[str]):
        """
        Initialize a new BaseAgent instance.
        
        Args:
            agent_id: Unique identifier for this agent.
            role: The role this agent fulfills (e.g., "PM", "Backend", "Frontend").
            capabilities: List of capabilities this agent has.
        """
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.state: Dict[str, Any] = {}
        self.message_history: List[Dict[str, Any]] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
    
    async def start(self):
        """Start the agent's task processing loop."""
        self.running = True
        await self._process_task_loop()
    
    async def stop(self):
        """Stop the agent's task processing loop."""
        self.running = False
    
    async def _process_task_loop(self):
        """Main processing loop for handling tasks."""
        while self.running:
            try:
                task = await self.task_queue.get()
                result = await self.process_task(task)
                self.task_queue.task_done()
                
                # If the task generated a response or notification, handle it
                if result and isinstance(result, dict) and result.get('type') == 'message':
                    await self._handle_outgoing_message(result)
            except Exception as e:
                print(f"Error processing task in agent {self.agent_id}: {str(e)}")
    
    async def receive_message(self, message: Dict[str, Any]) -> None:
        """
        Process an incoming message from another agent or system component.
        
        Args:
            message: The message to process, expected to be a dict with at least
                    'sender', 'recipient', 'content', and 'message_type' keys.
        """
        # Validate message format
        required_fields = ['sender', 'recipient', 'content', 'message_type', 'message_id', 'timestamp']
        for field in required_fields:
            if field not in message:
                print(f"Error: Received malformed message missing '{field}' field")
                return
        
        # Add to message history
        self.message_history.append(message)
        
        # Handle message based on its type
        if message['message_type'] == 'task':
            # Put the task in the queue for processing
            await self.task_queue.put(message)
        elif message['message_type'] == 'query':
            # Handle queries that need immediate response
            response = await self._handle_query(message)
            if response:
                await self.send_message(
                    recipient=message['sender'],
                    content=response,
                    message_type='response',
                    reply_to=message['message_id']
                )
        elif message['message_type'] == 'notification':
            # Just log notifications, no response needed
            print(f"Agent {self.agent_id} received notification: {message['content']}")
    
    async def send_message(
        self,
        recipient: str,
        content: Any,
        message_type: str = "standard",
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to another agent or component.
        
        Args:
            recipient: ID of the recipient agent or 'broadcast' for all agents.
            content: The message content, can be any JSON-serializable data.
            message_type: Type of message (standard, task, query, response, notification).
            reply_to: Optional ID of the message this is replying to.
            metadata: Optional additional metadata for the message.
            
        Returns:
            The created message dict.
        """
        message = {
            'message_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'sender': self.agent_id,
            'recipient': recipient,
            'message_type': message_type,
            'content': content,
            'reply_to': reply_to,
            'metadata': metadata or {}
        }
        
        # Add to our message history
        self.message_history.append(message)
        
        # This would normally call a messaging service to deliver the message
        # For now, we'll just return the message for handling by the caller
        return {
            'type': 'message',
            'payload': message
        }
    
    async def _handle_query(self, message: Dict[str, Any]) -> Any:
        """
        Handle query messages that require an immediate response.
        
        Args:
            message: The query message to handle.
            
        Returns:
            The response data, or None if the query couldn't be handled.
        """
        query_type = message.get('content', {}).get('query_type')
        
        if query_type == 'status':
            return {
                'status': 'active' if self.running else 'inactive',
                'role': self.role,
                'capabilities': self.capabilities,
                'queue_size': self.task_queue.qsize()
            }
        elif query_type == 'capabilities':
            return {
                'role': self.role,
                'capabilities': self.capabilities
            }
        
        # Default: we don't know how to handle this query
        return None
    
    async def _handle_outgoing_message(self, message_result: Dict[str, Any]) -> None:
        """
        Handle an outgoing message result from task processing.
        In a real implementation, this would interface with a message bus.
        
        Args:
            message_result: The message result to handle.
        """
        # In a real implementation, this would send the message via a message bus
        # For now, just log that we would send this message
        message = message_result['payload']
        print(f"Agent {self.agent_id} would send message of type {message['message_type']} to {message['recipient']}")
    
    async def process_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a task received from another agent or component.
        This should be overridden by specialized agents to implement their specific logic.
        
        Args:
            task: The task to process, expected to be a dict with task details.
            
        Returns:
            Optional result of the task processing, which might be a message to send.
        """
        # Check if this is an internal task without sender/message_id
        if 'sender' not in task or 'message_id' not in task:
            # For internal tasks, just return a default response
            return {
                'status': 'acknowledged',
                'message': f"Agent {self.agent_id} processed an internal task of type {task.get('type', 'unknown')}",
                'result': {}
            }
            
        # Base implementation for external messages just acknowledges receipt
        return await self.send_message(
            recipient=task['sender'],
            content={
                'status': 'acknowledged',
                'message': f"Agent {self.agent_id} has received the task but has no specific implementation."
            },
            message_type='response',
            reply_to=task['message_id']
        )
    
    async def save_state(self) -> Dict[str, Any]:
        """
        Save the current state of the agent.
        
        Returns:
            The state data that was saved.
        """
        state_data = {
            'agent_id': self.agent_id,
            'role': self.role,
            'capabilities': self.capabilities,
            'state': self.state,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # In a real implementation, this would persist the state to storage
        # For now, just return the state data
        return state_data
    
    async def load_state(self, state_id: str) -> bool:
        """
        Load the agent state from persistent storage.
        
        Args:
            state_id: Identifier for the state to load.
            
        Returns:
            True if the state was loaded successfully, False otherwise.
        """
        # In a real implementation, this would retrieve state from storage
        # For now, always return False to indicate state loading is not implemented
        return False
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.role} Agent ({self.agent_id})"