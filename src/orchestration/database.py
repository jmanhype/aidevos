"""
AIDevOS Database Models and Data Access Layer

This module defines the database models and data access patterns for the AIDevOS system.
It provides a clean interface for storing and retrieving data while abstracting the underlying
database implementation.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Callable

# Type variables for generic database operations
T = TypeVar('T')
ID = TypeVar('ID')


class Model:
    """Base class for all database models"""
    
    def __init__(self):
        """Initialize a new model instance"""
        if not hasattr(self, 'id'):
            self.id = str(uuid.uuid4())
        
        if not hasattr(self, 'created_at'):
            self.created_at = datetime.utcnow().isoformat()
        
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary format
        
        Returns:
            Dictionary representation of the model
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """
        Create model instance from dictionary
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            Model instance
        """
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


class User(Model):
    """User model representing a system user"""
    
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        roles: List[str] = None,
        first_name: str = None,
        last_name: str = None,
        settings: Dict[str, Any] = None
    ):
        """
        Initialize a new User instance
        
        Args:
            username: Unique username for this user
            email: User's email address
            password_hash: Hashed password for authentication
            roles: List of roles assigned to this user
            first_name: User's first name (optional)
            last_name: User's last name (optional)
            settings: User-specific settings (optional)
        """
        super().__init__()
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.roles = roles or ['user']
        self.first_name = first_name
        self.last_name = last_name
        self.settings = settings or {}
        self.last_login = None
        self.is_active = True


class Project(Model):
    """Project model representing a development project"""
    
    def __init__(
        self,
        name: str,
        description: str,
        owner_id: str,
        repository_url: Optional[str] = None,
        settings: Dict[str, Any] = None,
        members: List[str] = None
    ):
        """
        Initialize a new Project instance
        
        Args:
            name: Project name
            description: Project description
            owner_id: ID of the user who owns this project
            repository_url: URL to the project repository (optional)
            settings: Project-specific settings (optional)
            members: List of user IDs who are project members (optional)
        """
        super().__init__()
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.repository_url = repository_url
        self.settings = settings or {}
        self.members = members or []
        self.status = 'active'


class DurableObject(Model):
    """Model representing a Durable Object instance"""
    
    def __init__(
        self,
        name: str,
        object_type: str,
        state: Dict[str, Any],
        project_id: str,
        version: str = '1.0.0',
        status: str = 'initializing'
    ):
        """
        Initialize a new DurableObject instance
        
        Args:
            name: Name of this Durable Object
            object_type: Type of Durable Object (e.g., 'auth', 'user', 'data')
            state: Current state of the Durable Object
            project_id: ID of the project this object belongs to
            version: Version of this Durable Object
            status: Current status (initializing, active, hibernating, terminating)
        """
        super().__init__()
        self.name = name
        self.object_type = object_type
        self.state = state
        self.project_id = project_id
        self.version = version
        self.status = status
        self.last_activity = datetime.utcnow().isoformat()


class APIKey(Model):
    """Model representing an API key for external access"""
    
    def __init__(
        self,
        key: str,
        user_id: str,
        project_id: Optional[str] = None,
        permissions: List[str] = None,
        name: str = 'Default API Key',
        expires_at: Optional[str] = None
    ):
        """
        Initialize a new APIKey instance
        
        Args:
            key: The API key value (should be hashed before storing)
            user_id: ID of the user who owns this key
            project_id: Optional ID of the project this key is for
            permissions: List of permissions granted to this key
            name: Human-readable name for this key
            expires_at: Optional expiration date in ISO format
        """
        super().__init__()
        self.key = key
        self.user_id = user_id
        self.project_id = project_id
        self.permissions = permissions or ['read']
        self.name = name
        self.expires_at = expires_at
        self.last_used = None
        self.is_active = True


class Task(Model):
    """Model representing a task or unit of work"""
    
    def __init__(
        self,
        title: str,
        description: str,
        project_id: str,
        assigned_to: Optional[str] = None,
        created_by: Optional[str] = None,
        priority: int = 1,
        status: str = 'open',
        due_date: Optional[str] = None,
        tags: List[str] = None
    ):
        """
        Initialize a new Task instance
        
        Args:
            title: Task title
            description: Task description
            project_id: ID of the project this task belongs to
            assigned_to: Optional ID of the user assigned to this task
            created_by: Optional ID of the user who created this task
            priority: Task priority (1-5, 5 being highest)
            status: Task status (open, in_progress, review, done)
            due_date: Optional due date in ISO format
            tags: Optional list of tags
        """
        super().__init__()
        self.title = title
        self.description = description
        self.project_id = project_id
        self.assigned_to = assigned_to
        self.created_by = created_by
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.tags = tags or []
        self.completed_at = None


class DataStore(Generic[T, ID]):
    """
    Generic data store interface providing CRUD operations
    
    This abstract class defines the interface for data storage operations.
    Concrete implementations will provide the actual storage mechanism.
    """
    
    async def create(self, item: T) -> T:
        """
        Create a new item in the data store
        
        Args:
            item: The item to create
            
        Returns:
            The created item
        """
        raise NotImplementedError
    
    async def read(self, id: ID) -> Optional[T]:
        """
        Read an item from the data store by ID
        
        Args:
            id: The ID of the item to read
            
        Returns:
            The item if found, None otherwise
        """
        raise NotImplementedError
    
    async def update(self, id: ID, item: T) -> Optional[T]:
        """
        Update an item in the data store
        
        Args:
            id: The ID of the item to update
            item: The updated item
            
        Returns:
            The updated item if found, None otherwise
        """
        raise NotImplementedError
    
    async def delete(self, id: ID) -> bool:
        """
        Delete an item from the data store
        
        Args:
            id: The ID of the item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        raise NotImplementedError
    
    async def list(self, filter_func: Optional[Callable[[T], bool]] = None) -> List[T]:
        """
        List items from the data store, optionally filtered
        
        Args:
            filter_func: Optional function to filter items
            
        Returns:
            List of items matching the filter
        """
        raise NotImplementedError


class InMemoryDataStore(DataStore[T, ID]):
    """
    In-memory implementation of the DataStore interface
    
    This implementation uses an in-memory dictionary to store items.
    It's suitable for development, testing, or small-scale deployments.
    """
    
    def __init__(self):
        """Initialize a new in-memory data store"""
        self._store: Dict[ID, T] = {}
    
    async def create(self, item: T) -> T:
        """Create a new item in the store"""
        if hasattr(item, 'id'):
            self._store[getattr(item, 'id')] = item
        return item
    
    async def read(self, id: ID) -> Optional[T]:
        """Read an item from the store by ID"""
        return self._store.get(id)
    
    async def update(self, id: ID, item: T) -> Optional[T]:
        """Update an item in the store"""
        if id in self._store:
            if hasattr(item, 'updated_at'):
                setattr(item, 'updated_at', datetime.utcnow().isoformat())
            self._store[id] = item
            return item
        return None
    
    async def delete(self, id: ID) -> bool:
        """Delete an item from the store"""
        if id in self._store:
            del self._store[id]
            return True
        return False
    
    async def list(self, filter_func: Optional[Callable[[T], bool]] = None) -> List[T]:
        """List items from the store, optionally filtered"""
        items = list(self._store.values())
        if filter_func:
            items = [item for item in items if filter_func(item)]
        return items


# Database instances for different model types
user_store = InMemoryDataStore[User, str]()
project_store = InMemoryDataStore[Project, str]()
durable_object_store = InMemoryDataStore[DurableObject, str]()
api_key_store = InMemoryDataStore[APIKey, str]()
task_store = InMemoryDataStore[Task, str]()
"""