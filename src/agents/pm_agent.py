"""
PM (Product Manager) Agent implementation for AIDevOS.

This module defines the PM Agent, responsible for system design, feature planning,
and architecture in the AIDevOS system.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class PMAgent(BaseAgent):
    """
    PM (Product Manager) Agent responsible for system design, feature planning,
    and architecture in the AIDevOS system.
    
    The PM Agent coordinates the activities of other specialized agents and maintains
    the overall system vision and roadmap.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize a new PM Agent.
        
        Args:
            agent_id: Unique identifier for this agent.
        """
        capabilities = [
            "architecture_design",
            "feature_planning",
            "task_assignment",
            "progress_tracking",
            "documentation",
            "agent_coordination"
        ]
        super().__init__(agent_id, "PM", capabilities)
        
        # PM-specific state
        self.state.update({
            "current_features": [],
            "assigned_tasks": {},
            "architecture_decisions": [],
            "tracked_progress": {}
        })
    
    async def process_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a task assigned to the PM Agent.
        
        Args:
            task: The task to process, containing task details.
            
        Returns:
            Optional result of the task processing, which might be a message to send.
        """
        # Get task type from the direct task dictionary, supporting both content.task_type and type
        task_type = task.get('type', task.get('content', {}).get('task_type'))
        
        if task_type == 'requirements_analysis':
            return await self._handle_requirements_analysis(task)
        elif task_type == 'architecture_design':
            return await self._handle_architecture_design(task)
        elif task_type == 'feature_planning':
            return await self._handle_feature_planning(task)
        elif task_type == 'task_assignment':
            return await self._handle_task_assignment(task)
        elif task_type == 'progress_tracking':
            return await self._handle_progress_tracking(task)
        elif task_type == 'architecture_decision':
            return await self._handle_architecture_decision(task)
        elif task_type == 'architecture_finalization':
            return await self._handle_architecture_finalization(task)
        
        # If we don't recognize the task type, use the default behavior
        return await super().process_task(task)
    
    async def _handle_requirements_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle requirements analysis tasks.
        
        Args:
            task: The requirements analysis task details.
            
        Returns:
            The result of processing the requirements analysis task.
        """
        # Extract project description from the task
        description = task.get('description', '')
        
        # In a real implementation, this would involve analyzing the requirements
        # For demonstration, we'll return a simple requirements structure
        requirements = {
            "name": "Notification System",
            "description": "A system for managing and delivering notifications to users",
            "functional_requirements": [
                {
                    "id": "FR-1",
                    "name": "Notification Creation",
                    "description": "System should allow creating notifications with different priorities"
                },
                {
                    "id": "FR-2",
                    "name": "Notification Delivery",
                    "description": "System should support multiple delivery channels (email, SMS, in-app)"
                },
                {
                    "id": "FR-3",
                    "name": "Notification Templates",
                    "description": "System should support customizable notification templates"
                },
                {
                    "id": "FR-4",
                    "name": "Delivery Status Tracking",
                    "description": "System should track and report delivery status of notifications"
                }
            ],
            "non_functional_requirements": [
                {
                    "id": "NFR-1",
                    "name": "Performance",
                    "description": "System should handle at least 1000 notifications per minute"
                },
                {
                    "id": "NFR-2",
                    "name": "Reliability",
                    "description": "System should have 99.9% uptime"
                },
                {
                    "id": "NFR-3",
                    "name": "Security",
                    "description": "All notification data should be encrypted at rest and in transit"
                }
            ],
            "constraints": [
                {
                    "id": "CON-1",
                    "name": "Compliance",
                    "description": "System must comply with data protection regulations"
                },
                {
                    "id": "CON-2",
                    "name": "Integration",
                    "description": "System must integrate with existing user management system"
                }
            ],
            "stakeholders": [
                {
                    "id": "SH-1",
                    "name": "End Users",
                    "needs": "Receive timely and relevant notifications"
                },
                {
                    "id": "SH-2",
                    "name": "Administrators",
                    "needs": "Manage notification settings and monitor delivery"
                }
            ]
        }
        
        # Update state with the requirements
        self.state.update({
            "current_project": requirements["name"],
            "current_requirements": requirements
        })
        
        return requirements
        
    async def _handle_architecture_design(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle architecture design tasks.
        
        Args:
            task: The architecture design task details.
            
        Returns:
            The result of processing the architecture design task.
        """
        # Extract task details
        content = task.get('content', {})
        component = content.get('component', 'unknown')
        requirements = task.get('requirements', content.get('requirements', []))
        
        # In a real implementation, this would involve complex processing to design architecture
        # For now, we'll just acknowledge the task and store minimal information
        
        # Store this architecture component in our state
        if 'architecture_components' not in self.state:
            self.state['architecture_components'] = {}
        
        self.state['architecture_components'][component] = {
            'requirements': requirements,
            'status': 'in_progress',
            'assigned_at': task.get('timestamp', datetime.now().isoformat())
        }
        
        # Create architecture proposal
        architecture = {
            "name": "Notification System Architecture",
            "version": "0.1.0",
            "description": "Initial architecture for a scalable notification system",
            "components": [
                {
                    "name": "NotificationAPI",
                    "type": "service",
                    "description": "REST API for notification management",
                    "technologies": ["Python", "FastAPI", "OpenAPI"]
                },
                {
                    "name": "NotificationProcessor",
                    "type": "service",
                    "description": "Background service for processing and routing notifications",
                    "technologies": ["Python", "Redis", "Celery"]
                },
                {
                    "name": "NotificationDelivery",
                    "type": "service",
                    "description": "Service for delivering notifications via different channels",
                    "technologies": ["Python", "SMTP", "Twilio", "WebSockets"]
                }
            ],
            "data_model": {
                "Notification": {
                    "id": "string",
                    "type": "string",
                    "content": "string",
                    "recipient": "string",
                    "status": "string",
                    "created_at": "datetime",
                    "delivered_at": "datetime"
                },
                "NotificationTemplate": {
                    "id": "string",
                    "name": "string",
                    "content_template": "string",
                    "variables": "array"
                },
                "DeliveryChannel": {
                    "id": "string",
                    "type": "string",
                    "config": "object"
                }
            },
            "apis": {
                "internal": [
                    "/api/internal/notifications",
                    "/api/internal/templates",
                    "/api/internal/channels"
                ],
                "external": [
                    "/api/v1/notifications",
                    "/api/v1/status"
                ]
            }
        }
        
        # If task has sender, send a response, otherwise just return the architecture
        if 'sender' in task:
            return await self.send_message(
                recipient=task['sender'],
                content={
                    'status': 'in_progress',
                    'message': f"PM Agent has started architecture design for {component}",
                    'estimated_completion': "2025-03-15T00:00:00Z",  # Example fixed date
                    'architecture': architecture
                },
                message_type='response',
                reply_to=task.get('message_id')
            )
        else:
            return architecture
    
    async def _handle_feature_planning(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle feature planning tasks.
        
        Args:
            task: The feature planning task details.
            
        Returns:
            The result of processing the feature planning task.
        """
        # Extract task details
        content = task.get('content', {})
        feature_name = content.get('feature_name', 'unknown')
        feature_description = content.get('feature_description', '')
        priority = content.get('priority', 'medium')
        
        # Add this feature to our tracked features
        if feature_name not in [f.get('name') for f in self.state['current_features']]:
            self.state['current_features'].append({
                'name': feature_name,
                'description': feature_description,
                'priority': priority,
                'status': 'planned',
                'created_at': task.get('timestamp')
            })
        
        # Respond with acknowledgment
        return await self.send_message(
            recipient=task['sender'],
            content={
                'status': 'planned',
                'message': f"Feature '{feature_name}' has been added to the planning backlog with {priority} priority.",
                'feature_id': len(self.state['current_features']) - 1
            },
            message_type='response',
            reply_to=task['message_id']
        )
    
    async def _handle_task_assignment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task assignment requests.
        
        Args:
            task: The task assignment details.
            
        Returns:
            The result of processing the task assignment.
        """
        # Extract task details
        content = task.get('content', {})
        task_name = content.get('task_name', 'unknown')
        assignee = content.get('assignee', '')
        description = content.get('description', '')
        due_date = content.get('due_date')
        
        # Track this assignment in our state
        if assignee not in self.state['assigned_tasks']:
            self.state['assigned_tasks'][assignee] = []
        
        task_id = f"task_{len(self.state['assigned_tasks'][assignee])}"
        self.state['assigned_tasks'][assignee].append({
            'id': task_id,
            'name': task_name,
            'description': description,
            'due_date': due_date,
            'status': 'assigned',
            'assigned_at': task.get('timestamp')
        })
        
        # Send a task message to the assignee
        await self.send_message(
            recipient=assignee,
            content={
                'task_type': 'assigned_work',
                'task_id': task_id,
                'task_name': task_name,
                'description': description,
                'due_date': due_date
            },
            message_type='task'
        )
        
        # Respond to the requester
        return await self.send_message(
            recipient=task['sender'],
            content={
                'status': 'assigned',
                'message': f"Task '{task_name}' has been assigned to {assignee}.",
                'task_id': task_id
            },
            message_type='response',
            reply_to=task['message_id']
        )
    
    async def _handle_progress_tracking(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle progress tracking updates.
        
        Args:
            task: The progress tracking details.
            
        Returns:
            The result of processing the progress update.
        """
        # Extract task details
        content = task.get('content', {})
        component = content.get('component', 'unknown')
        progress = content.get('progress', 0)
        status = content.get('status', 'in_progress')
        notes = content.get('notes', '')
        
        # Update our tracked progress
        self.state['tracked_progress'][component] = {
            'progress': progress,
            'status': status,
            'notes': notes,
            'updated_at': task.get('timestamp')
        }
        
        # Respond with acknowledgment
        return await self.send_message(
            recipient=task['sender'],
            content={
                'status': 'updated',
                'message': f"Progress for {component} updated to {progress}% ({status})."
            },
            message_type='response',
            reply_to=task['message_id']
        )
    
    async def _handle_architecture_decision(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle architecture decision records.
        
        Args:
            task: The architecture decision details.
            
        Returns:
            The result of processing the architecture decision.
        """
        # Extract task details
        content = task.get('content', {})
        decision_id = content.get('decision_id', f"ADR-{len(self.state['architecture_decisions']) + 1}")
        title = content.get('title', 'Unnamed Decision')
        context = content.get('context', '')
        decision = content.get('decision', '')
        consequences = content.get('consequences', '')
        status = content.get('status', 'proposed')
        
        # Add to our tracked architecture decisions
        self.state['architecture_decisions'].append({
            'id': decision_id,
            'title': title,
            'context': context,
            'decision': decision,
            'consequences': consequences,
            'status': status,
            'created_at': task.get('timestamp')
        })
        
        # For significant decisions, notify other agents
        if status in ['accepted', 'approved']:
            # Broadcast to all agents about this decision
            await self.send_message(
                recipient='broadcast',
                content={
                    'notification_type': 'architecture_decision',
                    'decision_id': decision_id,
                    'title': title,
                    'status': status,
                    'summary': f"Architecture Decision: {title} has been {status}."
                },
                message_type='notification'
            )
        
        # Respond with acknowledgment
        return await self.send_message(
            recipient=task['sender'],
            content={
                'status': 'recorded',
                'message': f"Architecture decision '{title}' has been recorded with status '{status}'.",
                'decision_id': decision_id
            },
            message_type='response',
            reply_to=task['message_id']
        )
    
    async def _handle_architecture_finalization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle architecture finalization tasks.
        
        Args:
            task: The architecture finalization task details.
            
        Returns:
            The result of finalized architecture.
        """
        # Extract task details
        initial_architecture = task.get('initial_architecture', {})
        feedback = task.get('feedback', [])
        
        # In a real implementation, this would involve incorporating feedback
        # into the initial architecture design
        
        # For demonstration, we'll return a simple finalized architecture
        finalized_architecture = {
            "name": "Notification System Architecture",
            "version": "1.0.0",
            "description": "Architecture for a scalable notification system",
            "components": [
                {
                    "name": "NotificationAPI",
                    "type": "service",
                    "description": "REST API for notification management",
                    "technologies": ["Python", "FastAPI", "OpenAPI"]
                },
                {
                    "name": "NotificationProcessor",
                    "type": "service",
                    "description": "Background service for processing and routing notifications",
                    "technologies": ["Python", "Redis", "Celery"]
                },
                {
                    "name": "NotificationDelivery",
                    "type": "service",
                    "description": "Service for delivering notifications via different channels",
                    "technologies": ["Python", "SMTP", "Twilio", "WebSockets"]
                },
                {
                    "name": "NotificationStorage",
                    "type": "database",
                    "description": "Database for storing notification data",
                    "technologies": ["PostgreSQL", "Redis"]
                },
                {
                    "name": "AdminDashboard",
                    "type": "ui",
                    "description": "Web interface for managing notifications",
                    "technologies": ["React", "TypeScript", "Material-UI"]
                }
            ],
            "services": [
                {
                    "name": "NotificationService",
                    "description": "Core service for managing notifications",
                    "endpoints": [
                        "/api/notifications",
                        "/api/notifications/{id}",
                        "/api/notifications/templates",
                        "/api/notifications/status"
                    ],
                    "dependencies": ["NotificationStorage", "NotificationProcessor"]
                },
                {
                    "name": "TemplateService",
                    "description": "Service for managing notification templates",
                    "endpoints": [
                        "/api/templates",
                        "/api/templates/{id}",
                        "/api/templates/render"
                    ],
                    "dependencies": ["NotificationStorage"]
                },
                {
                    "name": "DeliveryService",
                    "description": "Service for delivering notifications",
                    "endpoints": [
                        "/api/delivery/status",
                        "/api/delivery/channels",
                        "/api/delivery/retry"
                    ],
                    "dependencies": ["NotificationProcessor", "NotificationStorage"]
                }
            ],
            "data_flow": [
                {
                    "from": "NotificationAPI",
                    "to": "NotificationProcessor",
                    "description": "API sends notification requests to processor"
                },
                {
                    "from": "NotificationProcessor",
                    "to": "NotificationDelivery",
                    "description": "Processor sends formatted notifications to delivery service"
                },
                {
                    "from": "NotificationDelivery",
                    "to": "External Systems",
                    "description": "Delivery service sends notifications to external channels"
                }
            ],
            "deployment": {
                "infrastructure": "Kubernetes",
                "scaling": "Horizontal pod autoscaling",
                "regions": ["us-west", "us-east", "eu-central"],
                "monitoring": "Prometheus + Grafana",
                "logging": "ELK Stack"
            }
        }
        
        # Incorporate feedback - in a real system this would be more sophisticated
        for fb in feedback:
            if isinstance(fb, dict) and "recommendations" in fb:
                if "design_considerations" not in finalized_architecture:
                    finalized_architecture["design_considerations"] = []
                
                if isinstance(fb["recommendations"], list):
                    finalized_architecture["design_considerations"].extend(fb["recommendations"])
        
        # Update state with the finalized architecture
        self.state["finalized_architecture"] = finalized_architecture
        
        return finalized_architecture
    
    def get_current_roadmap(self) -> List[Dict[str, Any]]:
        """
        Get the current feature roadmap.
        
        Returns:
            List of features in the current roadmap.
        """
        return sorted(self.state['current_features'], key=lambda x: {
            'high': 0,
            'medium': 1,
            'low': 2
        }.get(x.get('priority', 'medium'), 1))
    
    def get_architecture_decisions(self) -> List[Dict[str, Any]]:
        """
        Get all recorded architecture decisions.
        
        Returns:
            List of architecture decisions.
        """
        return self.state['architecture_decisions']