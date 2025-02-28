"""
AIDevOS Durable Objects Framework

This module implements the Durable Objects framework for AIDevOS, providing
a microservices-like architecture with persistent, isolated units of computation.
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Callable, Union

from .database import DurableObject, durable_object_store, user_store, project_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variable for the durable object class
T = TypeVar('T', bound='BaseDurableObject')


class BaseDurableObject(ABC):
    """
    Base class for all Durable Objects in AIDevOS
    
    Durable Objects are isolated, self-contained units of computation that
    maintain their own state and respond to requests. They are the backbone
    of the microservices architecture in AIDevOS.
    """
    
    def __init__(
        self,
        object_id: str,
        project_id: str,
        name: str,
        state: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new Durable Object
        
        Args:
            object_id: Unique identifier for this object
            project_id: ID of the project this object belongs to
            name: Human-readable name for this object
            state: Initial state for this object (optional)
        """
        self.object_id = object_id
        self.project_id = project_id
        self.name = name
        self.state = state or {}
        self._status = "initializing"
        self._version = "1.0.0"
        self._created_at = datetime.utcnow().isoformat()
        self._updated_at = self._created_at
        self._last_activity = self._created_at
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._subscribed_events: Set[str] = set()
    
    @property
    def status(self) -> str:
        """Get the current status of this Durable Object"""
        return self._status
    
    @status.setter
    def status(self, value: str) -> None:
        """Set the status of this Durable Object"""
        if value not in ["initializing", "active", "idle", "hibernating", "terminating"]:
            raise ValueError(f"Invalid status: {value}")
        self._status = value
        self._updated_at = datetime.utcnow().isoformat()
    
    async def initialize(self) -> None:
        """
        Initialize this Durable Object
        
        This method is called when the object is created or activated.
        It should set up any resources or connections needed by the object.
        """
        self.status = "active"
        await self._save_state()
        logger.info(f"Durable Object {self.name} ({self.object_id}) initialized")
    
    async def process_request(
        self,
        action: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a request to this Durable Object
        
        Args:
            action: The action to perform
            data: The data for the action
            metadata: Optional metadata for the request
            
        Returns:
            Response data from the action
        """
        self._last_activity = datetime.utcnow().isoformat()
        
        # Update object status if it's hibernating
        if self._status == "hibernating":
            await self.initialize()
        elif self._status != "active":
            return {"error": f"Object is {self._status} and cannot process requests"}
        
        # Process the request
        try:
            method_name = f"handle_{action}"
            if hasattr(self, method_name) and callable(getattr(self, method_name)):
                handler = getattr(self, method_name)
                response = await handler(data, metadata)
                await self._save_state()
                return response
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Error processing request {action} for object {self.object_id}: {str(e)}")
            return {"error": str(e)}
    
    async def hibernate(self) -> None:
        """
        Hibernate this Durable Object
        
        This method is called when the object is idle for too long.
        It should clean up any resources that shouldn't persist while hibernating.
        """
        self.status = "hibernating"
        await self._save_state()
        logger.info(f"Durable Object {self.name} ({self.object_id}) hibernated")
    
    async def terminate(self) -> None:
        """
        Terminate this Durable Object
        
        This method is called when the object is being destroyed.
        It should clean up all resources and save any final state.
        """
        self.status = "terminating"
        await self._save_state()
        logger.info(f"Durable Object {self.name} ({self.object_id}) terminated")
    
    async def _save_state(self) -> None:
        """Save the current state of this Durable Object to the data store"""
        # Create or update the DurableObject record
        db_object = DurableObject(
            name=self.name,
            object_type=self.__class__.__name__,
            state=self.state,
            project_id=self.project_id,
            version=self._version,
            status=self._status
        )
        db_object.id = self.object_id
        db_object.created_at = self._created_at
        db_object.updated_at = datetime.utcnow().isoformat()
        db_object.last_activity = self._last_activity
        
        # Store the object in the data store
        await durable_object_store.update(self.object_id, db_object)
    
    async def _load_state(self) -> None:
        """Load the state of this Durable Object from the data store"""
        db_object = await durable_object_store.read(self.object_id)
        if db_object:
            self.state = db_object.state
            self._status = db_object.status
            self._version = db_object.version
            self._created_at = db_object.created_at
            self._updated_at = db_object.updated_at
            self._last_activity = db_object.last_activity
    
    def subscribe_to_event(self, event_type: str) -> None:
        """
        Subscribe to an event
        
        Args:
            event_type: The type of event to subscribe to
        """
        self._subscribed_events.add(event_type)
    
    def unsubscribe_from_event(self, event_type: str) -> None:
        """
        Unsubscribe from an event
        
        Args:
            event_type: The type of event to unsubscribe from
        """
        if event_type in self._subscribed_events:
            self._subscribed_events.remove(event_type)
    
    async def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Handle an event received from the event bus
        
        Args:
            event_type: The type of event
            event_data: The event data
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Error handling event {event_type} in object {self.object_id}: {str(e)}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for an event type
        
        Args:
            event_type: The type of event to handle
            handler: The function to call when the event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        # Automatically subscribe to this event type
        self.subscribe_to_event(event_type)


class DurableObjectRegistry:
    """
    Registry for Durable Object types and instances
    
    This class manages the registration of Durable Object types and
    keeps track of active Durable Object instances.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton instance"""
        if cls._instance is None:
            cls._instance = super(DurableObjectRegistry, cls).__new__(cls)
            cls._instance._object_types: Dict[str, Type[BaseDurableObject]] = {}
            cls._instance._active_objects: Dict[str, BaseDurableObject] = {}
        return cls._instance
    
    def register_object_type(self, name: str, object_class: Type[BaseDurableObject]) -> None:
        """
        Register a Durable Object type
        
        Args:
            name: Name identifier for this object type
            object_class: Class of the Durable Object
        """
        self._object_types[name] = object_class
        logger.info(f"Registered Durable Object type: {name}")
    
    async def create_object(
        self,
        type_name: str,
        project_id: str,
        name: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new Durable Object instance
        
        Args:
            type_name: Type name of the object to create
            project_id: ID of the project this object belongs to
            name: Human-readable name for this object
            initial_state: Initial state for this object (optional)
            
        Returns:
            ID of the created object
        """
        if type_name not in self._object_types:
            raise ValueError(f"Unknown Durable Object type: {type_name}")
        
        # Create a new object
        object_id = str(uuid.uuid4())
        object_class = self._object_types[type_name]
        new_object = object_class(
            object_id=object_id,
            project_id=project_id,
            name=name,
            state=initial_state or {}
        )
        
        # Initialize the object
        await new_object.initialize()
        
        # Store in active objects
        self._active_objects[object_id] = new_object
        
        logger.info(f"Created Durable Object: {name} ({object_id}) of type {type_name}")
        return object_id
    
    async def get_object(self, object_id: str) -> Optional[BaseDurableObject]:
        """
        Get a Durable Object by ID
        
        Args:
            object_id: ID of the object to get
            
        Returns:
            The Durable Object if found, None otherwise
        """
        # Check if the object is already active
        if object_id in self._active_objects:
            return self._active_objects[object_id]
        
        # Try to load from data store
        db_object = await durable_object_store.read(object_id)
        if not db_object:
            return None
        
        # Get the object type
        object_type = db_object.object_type
        if object_type not in self._object_types:
            logger.error(f"Unknown object type: {object_type} for object ID: {object_id}")
            return None
        
        # Create and initialize the object
        object_class = self._object_types[object_type]
        durable_object = object_class(
            object_id=object_id,
            project_id=db_object.project_id,
            name=db_object.name,
            state=db_object.state
        )
        
        # Restore the object's state
        await durable_object._load_state()
        
        # If the object was hibernating, initialize it
        if durable_object.status == "hibernating":
            await durable_object.initialize()
        
        # Store in active objects
        self._active_objects[object_id] = durable_object
        
        return durable_object
    
    async def update_object(
        self,
        object_id: str,
        updates: Dict[str, Any]
    ) -> Optional[BaseDurableObject]:
        """
        Update a Durable Object
        
        Args:
            object_id: ID of the object to update
            updates: Updates to apply to the object's state
            
        Returns:
            The updated object if found, None otherwise
        """
        durable_object = await self.get_object(object_id)
        if not durable_object:
            return None
        
        # Update the object's state
        durable_object.state.update(updates)
        await durable_object._save_state()
        
        return durable_object
    
    async def delete_object(self, object_id: str) -> bool:
        """
        Delete a Durable Object
        
        Args:
            object_id: ID of the object to delete
            
        Returns:
            True if the object was deleted, False otherwise
        """
        durable_object = await self.get_object(object_id)
        if not durable_object:
            return False
        
        # Terminate the object
        await durable_object.terminate()
        
        # Remove from active objects
        if object_id in self._active_objects:
            del self._active_objects[object_id]
        
        # Delete from data store
        await durable_object_store.delete(object_id)
        
        logger.info(f"Deleted Durable Object: {durable_object.name} ({object_id})")
        return True
    
    async def list_objects(
        self,
        project_id: Optional[str] = None,
        object_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List Durable Objects, optionally filtered
        
        Args:
            project_id: Optional project ID to filter by
            object_type: Optional object type to filter by
            status: Optional status to filter by
            
        Returns:
            List of Durable Object metadata
        """
        # Define filter function
        def filter_func(obj: DurableObject) -> bool:
            if project_id and obj.project_id != project_id:
                return False
            if object_type and obj.object_type != object_type:
                return False
            if status and obj.status != status:
                return False
            return True
        
        # Get objects from data store
        objects = await durable_object_store.list(filter_func)
        
        # Convert to metadata format
        result = []
        for obj in objects:
            result.append({
                "id": obj.id,
                "name": obj.name,
                "type": obj.object_type,
                "project_id": obj.project_id,
                "status": obj.status,
                "version": obj.version,
                "created_at": obj.created_at,
                "updated_at": obj.updated_at,
                "last_activity": obj.last_activity
            })
        
        return result


class DurableObjectRouter:
    """
    Router for Durable Object requests
    
    This class routes incoming requests to the appropriate Durable Object
    based on the request path and parameters.
    """
    
    def __init__(self, registry: DurableObjectRegistry):
        """
        Initialize a new router
        
        Args:
            registry: The Durable Object registry to use
        """
        self.registry = registry
    
    async def route_request(
        self,
        object_id: str,
        action: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route a request to a Durable Object
        
        Args:
            object_id: ID of the target object
            action: Action to perform
            data: Data for the action
            metadata: Optional request metadata
            
        Returns:
            Response from the object
        """
        durable_object = await self.registry.get_object(object_id)
        if not durable_object:
            return {"error": f"Object not found: {object_id}"}
        
        # Process the request and return the response
        return await durable_object.process_request(action, data, metadata)


class EventBus:
    """
    Event bus for communication between Durable Objects
    
    This class facilitates publish-subscribe communication between
    Durable Objects, allowing them to react to events from other objects.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton instance"""
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._registry = DurableObjectRegistry()
            cls._instance._subscriptions: Dict[str, Set[str]] = {}
        return cls._instance
    
    async def publish(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        source_id: Optional[str] = None
    ) -> None:
        """
        Publish an event to all subscribers
        
        Args:
            event_type: Type of the event
            event_data: Event data
            source_id: Optional ID of the source object
        """
        if event_type not in self._subscriptions:
            # No subscribers for this event type
            return
        
        # Add metadata to the event
        event_with_metadata = {
            "data": event_data,
            "metadata": {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "source_id": source_id
            }
        }
        
        # Deliver to all subscribers
        for subscriber_id in self._subscriptions[event_type]:
            try:
                subscriber = await self._registry.get_object(subscriber_id)
                if subscriber:
                    await subscriber.handle_event(event_type, event_with_metadata)
            except Exception as e:
                logger.error(f"Error delivering event {event_type} to subscriber {subscriber_id}: {str(e)}")
    
    def subscribe(self, object_id: str, event_type: str) -> None:
        """
        Subscribe an object to an event type
        
        Args:
            object_id: ID of the subscribing object
            event_type: Type of event to subscribe to
        """
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = set()
        self._subscriptions[event_type].add(object_id)
    
    def unsubscribe(self, object_id: str, event_type: Optional[str] = None) -> None:
        """
        Unsubscribe an object from events
        
        Args:
            object_id: ID of the object to unsubscribe
            event_type: Optional specific event type to unsubscribe from.
                        If None, unsubscribe from all events.
        """
        if event_type:
            # Unsubscribe from a specific event type
            if event_type in self._subscriptions and object_id in self._subscriptions[event_type]:
                self._subscriptions[event_type].remove(object_id)
        else:
            # Unsubscribe from all event types
            for event_subscriptions in self._subscriptions.values():
                if object_id in event_subscriptions:
                    event_subscriptions.remove(object_id)


# Create singleton instances
registry = DurableObjectRegistry()
router = DurableObjectRouter(registry)
event_bus = EventBus()


# Define Durable Object lifecycle management functions
async def create_durable_object(
    type_name: str,
    project_id: str,
    name: str,
    initial_state: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a new Durable Object
    
    Args:
        type_name: Type of Durable Object to create
        project_id: ID of the project this object belongs to
        name: Human-readable name for this object
        initial_state: Optional initial state for the object
        
    Returns:
        ID of the created object
    """
    return await registry.create_object(type_name, project_id, name, initial_state)


async def get_durable_object(object_id: str) -> Optional[BaseDurableObject]:
    """
    Get a Durable Object by ID
    
    Args:
        object_id: ID of the object to retrieve
        
    Returns:
        The Durable Object if found, None otherwise
    """
    return await registry.get_object(object_id)


async def update_durable_object(
    object_id: str,
    updates: Dict[str, Any]
) -> Optional[BaseDurableObject]:
    """
    Update a Durable Object's state
    
    Args:
        object_id: ID of the object to update
        updates: Updates to apply to the object's state
        
    Returns:
        The updated object if found, None otherwise
    """
    return await registry.update_object(object_id, updates)


async def delete_durable_object(object_id: str) -> bool:
    """
    Delete a Durable Object
    
    Args:
        object_id: ID of the object to delete
        
    Returns:
        True if the object was deleted, False otherwise
    """
    return await registry.delete_object(object_id)


async def list_durable_objects(
    project_id: Optional[str] = None,
    object_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List Durable Objects, optionally filtered
    
    Args:
        project_id: Optional project ID to filter by
        object_type: Optional object type to filter by
        status: Optional status to filter by
        
    Returns:
        List of Durable Object metadata
    """
    return await registry.list_objects(project_id, object_type, status)


async def send_request_to_object(
    object_id: str,
    action: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a request to a Durable Object
    
    Args:
        object_id: ID of the target object
        action: Action to perform
        data: Data for the action
        metadata: Optional request metadata
        
    Returns:
        Response from the object
    """
    return await router.route_request(object_id, action, data, metadata)


async def publish_event(
    event_type: str,
    event_data: Dict[str, Any],
    source_id: Optional[str] = None
) -> None:
    """
    Publish an event to all subscribers
    
    Args:
        event_type: Type of the event
        event_data: Event data
        source_id: Optional ID of the source object
    """
    await event_bus.publish(event_type, event_data, source_id)
"""