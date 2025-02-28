"""
AIDevOS API Service Layer

This module implements RESTful API services for the AIDevOS system, exposing
the functionality of Durable Objects through standard HTTP endpoints.
"""

import asyncio
import datetime
import json
import logging
from typing import Any, Dict, List, Optional, Union

# The API implementation would typically use a web framework like FastAPI, 
# but for demonstration purposes, we'll define the structure without 
# tying it to a specific framework.

from .durable_objects import (
    create_durable_object,
    get_durable_object,
    update_durable_object,
    delete_durable_object,
    list_durable_objects,
    send_request_to_object,
    publish_event
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIRouter:
    """
    Base API Router that defines routes and handlers
    
    This class serves as a base for more specific API routers,
    providing common functionality for defining and handling routes.
    """
    
    def __init__(self, prefix: str = ""):
        """
        Initialize a new router
        
        Args:
            prefix: URL prefix for all routes in this router
        """
        self.prefix = prefix
        self.routes: Dict[str, Dict[str, Any]] = {}
    
    def add_route(self, path: str, method: str, handler_func: Any, auth_required: bool = True):
        """
        Add a route to this router
        
        Args:
            path: URL path for this route
            method: HTTP method (GET, POST, PUT, DELETE)
            handler_func: Function to handle this route
            auth_required: Whether authentication is required
        """
        full_path = f"{self.prefix}{path}"
        if full_path not in self.routes:
            self.routes[full_path] = {}
        
        self.routes[full_path][method.upper()] = {
            "handler": handler_func,
            "auth_required": auth_required
        }
    
    def get_handler(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """
        Get the handler for a route
        
        Args:
            path: URL path
            method: HTTP method
            
        Returns:
            Handler config if found, None otherwise
        """
        if path in self.routes and method.upper() in self.routes[path]:
            return self.routes[path][method.upper()]
        return None


class AuthRouter(APIRouter):
    """API Router for authentication endpoints"""
    
    def __init__(self):
        """Initialize the auth router"""
        super().__init__("/auth")
        
        # Define routes
        self.add_route("/login", "POST", self.login, auth_required=False)
        self.add_route("/register", "POST", self.register, auth_required=False)
        self.add_route("/refresh", "POST", self.refresh_token, auth_required=False)
        self.add_route("/logout", "POST", self.logout)
    
    async def login(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle login request
        
        Args:
            request_data: Request data with username and password
            
        Returns:
            Authentication response
        """
        # Create or get the Authentication Durable Object
        auth_objects = await list_durable_objects(object_type="AuthenticationDO")
        
        if auth_objects and len(auth_objects) > 0:
            auth_id = auth_objects[0]["id"]
        else:
            # Create a new Authentication Durable Object
            auth_id = await create_durable_object(
                type_name="AuthenticationDO",
                project_id="system",
                name="System Authentication Service"
            )
        
        # Send the login request to the Authentication Durable Object
        response = await send_request_to_object(
            object_id=auth_id,
            action="handle_login",
            data=request_data
        )
        
        return response
    
    async def register(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle registration request
        
        Args:
            request_data: Registration data
            
        Returns:
            Registration response
        """
        # Create or get the Authentication Durable Object
        auth_objects = await list_durable_objects(object_type="AuthenticationDO")
        
        if auth_objects and len(auth_objects) > 0:
            auth_id = auth_objects[0]["id"]
        else:
            # Create a new Authentication Durable Object
            auth_id = await create_durable_object(
                type_name="AuthenticationDO",
                project_id="system",
                name="System Authentication Service"
            )
        
        # Send the registration request to the Authentication Durable Object
        response = await send_request_to_object(
            object_id=auth_id,
            action="handle_register",
            data=request_data
        )
        
        return response
    
    async def refresh_token(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle token refresh request
        
        Args:
            request_data: Request data with refresh token
            
        Returns:
            Token refresh response
        """
        # Create or get the Authentication Durable Object
        auth_objects = await list_durable_objects(object_type="AuthenticationDO")
        
        if auth_objects and len(auth_objects) > 0:
            auth_id = auth_objects[0]["id"]
        else:
            # Create a new Authentication Durable Object
            auth_id = await create_durable_object(
                type_name="AuthenticationDO",
                project_id="system",
                name="System Authentication Service"
            )
        
        # Send the token refresh request to the Authentication Durable Object
        response = await send_request_to_object(
            object_id=auth_id,
            action="handle_refresh_token",
            data=request_data
        )
        
        return response
    
    async def logout(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle logout request
        
        Args:
            request_data: Request data
            user: Authenticated user data
            
        Returns:
            Logout response
        """
        # Create or get the Authentication Durable Object
        auth_objects = await list_durable_objects(object_type="AuthenticationDO")
        
        if auth_objects and len(auth_objects) > 0:
            auth_id = auth_objects[0]["id"]
        else:
            # Create a new Authentication Durable Object
            auth_id = await create_durable_object(
                type_name="AuthenticationDO",
                project_id="system",
                name="System Authentication Service"
            )
        
        # Send the logout request to the Authentication Durable Object
        response = await send_request_to_object(
            object_id=auth_id,
            action="handle_logout",
            data={"user_id": user["sub"]}
        )
        
        return response


class UserRouter(APIRouter):
    """API Router for user management endpoints"""
    
    def __init__(self):
        """Initialize the user router"""
        super().__init__("/users")
        
        # Define routes
        self.add_route("", "GET", self.list_users)
        self.add_route("/{user_id}", "GET", self.get_user)
        self.add_route("/{user_id}", "PUT", self.update_user)
        self.add_route("/{user_id}/deactivate", "POST", self.deactivate_user)
        self.add_route("/{user_id}/activate", "POST", self.activate_user)
    
    async def list_users(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        List users
        
        Args:
            request_data: Request data with filter criteria
            user: Authenticated user data
            
        Returns:
            List of users
        """
        # Check if the user has permission to list users
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        # Create or get the User Management Durable Object
        user_mgmt_objects = await list_durable_objects(object_type="UserManagementDO")
        
        if user_mgmt_objects and len(user_mgmt_objects) > 0:
            user_mgmt_id = user_mgmt_objects[0]["id"]
        else:
            # Create a new User Management Durable Object
            user_mgmt_id = await create_durable_object(
                type_name="UserManagementDO",
                project_id="system",
                name="System User Management Service"
            )
        
        # Send the list users request to the User Management Durable Object
        response = await send_request_to_object(
            object_id=user_mgmt_id,
            action="handle_list_users",
            data=request_data
        )
        
        return response
    
    async def get_user(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a user
        
        Args:
            request_data: Request data with user ID
            user: Authenticated user data
            
        Returns:
            User data
        """
        user_id = request_data.get("user_id")
        
        # Check if the user has permission to get this user
        if user_id != user.get("sub") and "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        # Create or get the User Management Durable Object
        user_mgmt_objects = await list_durable_objects(object_type="UserManagementDO")
        
        if user_mgmt_objects and len(user_mgmt_objects) > 0:
            user_mgmt_id = user_mgmt_objects[0]["id"]
        else:
            # Create a new User Management Durable Object
            user_mgmt_id = await create_durable_object(
                type_name="UserManagementDO",
                project_id="system",
                name="System User Management Service"
            )
        
        # Send the get user request to the User Management Durable Object
        response = await send_request_to_object(
            object_id=user_mgmt_id,
            action="handle_get_user",
            data={"user_id": user_id}
        )
        
        return response
    
    async def update_user(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user
        
        Args:
            request_data: Request data with user ID and updates
            user: Authenticated user data
            
        Returns:
            Update result
        """
        user_id = request_data.get("user_id")
        updates = request_data.get("updates", {})
        
        # Check if the user has permission to update this user
        if user_id != user.get("sub") and "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        # Create or get the User Management Durable Object
        user_mgmt_objects = await list_durable_objects(object_type="UserManagementDO")
        
        if user_mgmt_objects and len(user_mgmt_objects) > 0:
            user_mgmt_id = user_mgmt_objects[0]["id"]
        else:
            # Create a new User Management Durable Object
            user_mgmt_id = await create_durable_object(
                type_name="UserManagementDO",
                project_id="system",
                name="System User Management Service"
            )
        
        # Send the update user request to the User Management Durable Object
        response = await send_request_to_object(
            object_id=user_mgmt_id,
            action="handle_update_user",
            data={"user_id": user_id, "updates": updates}
        )
        
        return response
    
    async def deactivate_user(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deactivate a user
        
        Args:
            request_data: Request data with user ID
            user: Authenticated user data
            
        Returns:
            Deactivation result
        """
        user_id = request_data.get("user_id")
        
        # Check if the user has permission to deactivate users
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        # Create or get the User Management Durable Object
        user_mgmt_objects = await list_durable_objects(object_type="UserManagementDO")
        
        if user_mgmt_objects and len(user_mgmt_objects) > 0:
            user_mgmt_id = user_mgmt_objects[0]["id"]
        else:
            # Create a new User Management Durable Object
            user_mgmt_id = await create_durable_object(
                type_name="UserManagementDO",
                project_id="system",
                name="System User Management Service"
            )
        
        # Send the deactivate user request to the User Management Durable Object
        response = await send_request_to_object(
            object_id=user_mgmt_id,
            action="handle_deactivate_user",
            data={"user_id": user_id}
        )
        
        return response
    
    async def activate_user(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activate a user
        
        Args:
            request_data: Request data with user ID
            user: Authenticated user data
            
        Returns:
            Activation result
        """
        user_id = request_data.get("user_id")
        
        # Check if the user has permission to activate users
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        # Create or get the User Management Durable Object
        user_mgmt_objects = await list_durable_objects(object_type="UserManagementDO")
        
        if user_mgmt_objects and len(user_mgmt_objects) > 0:
            user_mgmt_id = user_mgmt_objects[0]["id"]
        else:
            # Create a new User Management Durable Object
            user_mgmt_id = await create_durable_object(
                type_name="UserManagementDO",
                project_id="system",
                name="System User Management Service"
            )
        
        # Send the activate user request to the User Management Durable Object
        response = await send_request_to_object(
            object_id=user_mgmt_id,
            action="handle_activate_user",
            data={"user_id": user_id}
        )
        
        return response


class DataRouter(APIRouter):
    """API Router for data storage endpoints"""
    
    def __init__(self):
        """Initialize the data router"""
        super().__init__("/data")
        
        # Define routes
        self.add_route("/collections", "GET", self.list_collections)
        self.add_route("/collections/{collection}", "GET", self.query_collection)
        self.add_route("/collections/{collection}", "POST", self.store_data)
        self.add_route("/collections/{collection}/{item_id}", "GET", self.get_data)
        self.add_route("/collections/{collection}/{item_id}", "PUT", self.update_data)
        self.add_route("/collections/{collection}/{item_id}", "DELETE", self.delete_data)
    
    async def list_collections(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        List collections
        
        Args:
            request_data: Request data
            user: Authenticated user data
            
        Returns:
            List of collections
        """
        # Create or get the Data Storage Durable Object
        data_storage_objects = await list_durable_objects(object_type="DataStorageDO")
        
        if data_storage_objects and len(data_storage_objects) > 0:
            data_storage_id = data_storage_objects[0]["id"]
        else:
            # Create a new Data Storage Durable Object
            data_storage_id = await create_durable_object(
                type_name="DataStorageDO",
                project_id="system",
                name="System Data Storage Service"
            )
        
        # Send the list collections request to the Data Storage Durable Object
        response = await send_request_to_object(
            object_id=data_storage_id,
            action="handle_list_collections",
            data={}
        )
        
        return response
    
    async def query_collection(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query a collection
        
        Args:
            request_data: Request data with collection and query parameters
            user: Authenticated user data
            
        Returns:
            Query results
        """
        collection = request_data.get("collection")
        query = request_data.get("query", {})
        limit = request_data.get("limit")
        skip = request_data.get("skip", 0)
        
        # Create or get the Data Storage Durable Object
        data_storage_objects = await list_durable_objects(object_type="DataStorageDO")
        
        if data_storage_objects and len(data_storage_objects) > 0:
            data_storage_id = data_storage_objects[0]["id"]
        else:
            # Create a new Data Storage Durable Object
            data_storage_id = await create_durable_object(
                type_name="DataStorageDO",
                project_id="system",
                name="System Data Storage Service"
            )
        
        # Send the query data request to the Data Storage Durable Object
        response = await send_request_to_object(
            object_id=data_storage_id,
            action="handle_query_data",
            data={
                "collection": collection,
                "query": query,
                "limit": limit,
                "skip": skip
            }
        )
        
        return response
    
    async def store_data(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store data in a collection
        
        Args:
            request_data: Request data with collection and data
            user: Authenticated user data
            
        Returns:
            Storage result
        """
        collection = request_data.get("collection")
        data = request_data.get("data")
        
        # Create or get the Data Storage Durable Object
        data_storage_objects = await list_durable_objects(object_type="DataStorageDO")
        
        if data_storage_objects and len(data_storage_objects) > 0:
            data_storage_id = data_storage_objects[0]["id"]
        else:
            # Create a new Data Storage Durable Object
            data_storage_id = await create_durable_object(
                type_name="DataStorageDO",
                project_id="system",
                name="System Data Storage Service"
            )
        
        # Add metadata
        data_with_metadata = data.copy() if data else {}
        data_with_metadata["_created_by"] = user.get("sub")
        data_with_metadata["_created_at"] = datetime.datetime.utcnow().isoformat()
        
        # Send the store data request to the Data Storage Durable Object
        response = await send_request_to_object(
            object_id=data_storage_id,
            action="handle_store_data",
            data={
                "collection": collection,
                "data": data_with_metadata
            }
        )
        
        return response
    
    async def get_data(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get data from a collection
        
        Args:
            request_data: Request data with collection and item ID
            user: Authenticated user data
            
        Returns:
            Retrieved data
        """
        collection = request_data.get("collection")
        item_id = request_data.get("item_id")
        
        # Create or get the Data Storage Durable Object
        data_storage_objects = await list_durable_objects(object_type="DataStorageDO")
        
        if data_storage_objects and len(data_storage_objects) > 0:
            data_storage_id = data_storage_objects[0]["id"]
        else:
            # Create a new Data Storage Durable Object
            data_storage_id = await create_durable_object(
                type_name="DataStorageDO",
                project_id="system",
                name="System Data Storage Service"
            )
        
        # Send the retrieve data request to the Data Storage Durable Object
        response = await send_request_to_object(
            object_id=data_storage_id,
            action="handle_retrieve_data",
            data={
                "collection": collection,
                "id": item_id
            }
        )
        
        return response
    
    async def update_data(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data in a collection
        
        Args:
            request_data: Request data with collection, item ID, and updates
            user: Authenticated user data
            
        Returns:
            Update result
        """
        collection = request_data.get("collection")
        item_id = request_data.get("item_id")
        updates = request_data.get("updates", {})
        
        # Create or get the Data Storage Durable Object
        data_storage_objects = await list_durable_objects(object_type="DataStorageDO")
        
        if data_storage_objects and len(data_storage_objects) > 0:
            data_storage_id = data_storage_objects[0]["id"]
        else:
            # Create a new Data Storage Durable Object
            data_storage_id = await create_durable_object(
                type_name="DataStorageDO",
                project_id="system",
                name="System Data Storage Service"
            )
        
        # Add metadata
        updates_with_metadata = updates.copy()
        updates_with_metadata["_updated_by"] = user.get("sub")
        updates_with_metadata["_updated_at"] = datetime.datetime.utcnow().isoformat()
        
        # Send the update data request to the Data Storage Durable Object
        response = await send_request_to_object(
            object_id=data_storage_id,
            action="handle_update_data",
            data={
                "collection": collection,
                "id": item_id,
                "data": updates_with_metadata
            }
        )
        
        return response
    
    async def delete_data(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete data from a collection
        
        Args:
            request_data: Request data with collection and item ID
            user: Authenticated user data
            
        Returns:
            Delete result
        """
        collection = request_data.get("collection")
        item_id = request_data.get("item_id")
        
        # Create or get the Data Storage Durable Object
        data_storage_objects = await list_durable_objects(object_type="DataStorageDO")
        
        if data_storage_objects and len(data_storage_objects) > 0:
            data_storage_id = data_storage_objects[0]["id"]
        else:
            # Create a new Data Storage Durable Object
            data_storage_id = await create_durable_object(
                type_name="DataStorageDO",
                project_id="system",
                name="System Data Storage Service"
            )
        
        # Send the delete data request to the Data Storage Durable Object
        response = await send_request_to_object(
            object_id=data_storage_id,
            action="handle_delete_data",
            data={
                "collection": collection,
                "id": item_id
            }
        )
        
        return response


class ProjectRouter(APIRouter):
    """API Router for project management endpoints"""
    
    def __init__(self):
        """Initialize the project router"""
        super().__init__("/projects")
        
        # Define routes
        self.add_route("", "GET", self.list_projects)
        self.add_route("", "POST", self.create_project)
        self.add_route("/{project_id}", "GET", self.get_project)
        self.add_route("/{project_id}", "PUT", self.update_project)
        self.add_route("/{project_id}", "DELETE", self.delete_project)
        self.add_route("/{project_id}/members", "GET", self.list_members)
        self.add_route("/{project_id}/members", "POST", self.add_member)
        self.add_route("/{project_id}/members/{user_id}", "DELETE", self.remove_member)
    
    # Project router handlers would be implemented similarly to the
    # other routers, interacting with Durable Objects for project management.
    # For brevity, we'll omit the full implementation here.
    
    async def list_projects(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        List projects accessible to the user
        
        Args:
            request_data: Request data
            user: Authenticated user data
            
        Returns:
            List of projects
        """
        # This would typically query a ProjectManagementDO
        return {"success": True, "projects": []}
    
    async def create_project(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project
        
        Args:
            request_data: Project data
            user: Authenticated user data
            
        Returns:
            Created project
        """
        # This would typically create a project via ProjectManagementDO
        return {"success": True, "project": {"id": "new-project-id", "name": request_data.get("name")}}
    
    async def get_project(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Get a project by ID"""
        return {"success": True, "project": {"id": request_data.get("project_id")}}
    
    async def update_project(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project"""
        return {"success": True, "message": "Project updated"}
    
    async def delete_project(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a project"""
        return {"success": True, "message": "Project deleted"}
    
    async def list_members(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """List project members"""
        return {"success": True, "members": []}
    
    async def add_member(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Add a member to a project"""
        return {"success": True, "message": "Member added"}
    
    async def remove_member(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a member from a project"""
        return {"success": True, "message": "Member removed"}


class DurableObjectRouter(APIRouter):
    """API Router for Durable Object management endpoints"""
    
    def __init__(self):
        """Initialize the Durable Object router"""
        super().__init__("/durable-objects")
        
        # Define routes
        self.add_route("", "GET", self.list_objects)
        self.add_route("", "POST", self.create_object)
        self.add_route("/{object_id}", "GET", self.get_object)
        self.add_route("/{object_id}", "PUT", self.update_object)
        self.add_route("/{object_id}", "DELETE", self.delete_object)
        self.add_route("/{object_id}/request", "POST", self.send_request)
    
    async def list_objects(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        List Durable Objects
        
        Args:
            request_data: Filter criteria
            user: Authenticated user data
            
        Returns:
            List of Durable Objects
        """
        # Check if the user has permission to list objects
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        # Extract filter criteria
        project_id = request_data.get("project_id")
        object_type = request_data.get("object_type")
        status = request_data.get("status")
        
        # List objects with the provided filters
        objects = await list_durable_objects(
            project_id=project_id,
            object_type=object_type,
            status=status
        )
        
        return {
            "success": True,
            "objects": objects,
            "total": len(objects)
        }
    
    async def create_object(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Durable Object
        
        Args:
            request_data: Object creation data
            user: Authenticated user data
            
        Returns:
            Created object details
        """
        # Check if the user has permission to create objects
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        # Extract creation data
        type_name = request_data.get("type_name")
        project_id = request_data.get("project_id")
        name = request_data.get("name")
        initial_state = request_data.get("initial_state", {})
        
        if not type_name or not project_id or not name:
            return {"error": "Type name, project ID, and name are required"}
        
        # Create the object
        object_id = await create_durable_object(
            type_name=type_name,
            project_id=project_id,
            name=name,
            initial_state=initial_state
        )
        
        return {
            "success": True,
            "object_id": object_id,
            "message": f"Durable Object {name} created successfully"
        }
    
    async def get_object(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a Durable Object by ID
        
        Args:
            request_data: Request with object ID
            user: Authenticated user data
            
        Returns:
            Object details
        """
        # Check if the user has permission to view objects
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        object_id = request_data.get("object_id")
        
        # Get the object
        durable_object = await get_durable_object(object_id)
        if not durable_object:
            return {"error": f"Object not found: {object_id}"}
        
        # Get object details
        object_details = {
            "id": object_id,
            "name": durable_object.name,
            "project_id": durable_object.project_id,
            "status": durable_object.status,
            "type": durable_object.__class__.__name__,
            "created_at": durable_object._created_at,
            "updated_at": durable_object._updated_at,
            "last_activity": durable_object._last_activity
        }
        
        return {
            "success": True,
            "object": object_details
        }
    
    async def update_object(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a Durable Object's state
        
        Args:
            request_data: Object update data
            user: Authenticated user data
            
        Returns:
            Update result
        """
        # Check if the user has permission to update objects
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        object_id = request_data.get("object_id")
        updates = request_data.get("updates", {})
        
        if not updates:
            return {"error": "Updates are required"}
        
        # Update the object
        updated_object = await update_durable_object(object_id, updates)
        if not updated_object:
            return {"error": f"Object not found: {object_id}"}
        
        return {
            "success": True,
            "message": f"Object {object_id} updated successfully"
        }
    
    async def delete_object(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a Durable Object
        
        Args:
            request_data: Request with object ID
            user: Authenticated user data
            
        Returns:
            Delete result
        """
        # Check if the user has permission to delete objects
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        object_id = request_data.get("object_id")
        
        # Delete the object
        result = await delete_durable_object(object_id)
        if not result:
            return {"error": f"Object not found or could not be deleted: {object_id}"}
        
        return {
            "success": True,
            "message": f"Object {object_id} deleted successfully"
        }
    
    async def send_request(self, request_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to a Durable Object
        
        Args:
            request_data: Request data
            user: Authenticated user data
            
        Returns:
            Request result
        """
        # Check if the user has permission to send requests to objects
        if "admin" not in user.get("roles", []):
            return {"error": "Insufficient permissions"}
        
        object_id = request_data.get("object_id")
        action = request_data.get("action")
        data = request_data.get("data", {})
        
        if not action:
            return {"error": "Action is required"}
        
        # Send the request to the object
        response = await send_request_to_object(
            object_id=object_id,
            action=action,
            data=data,
            metadata={"user_id": user.get("sub")}
        )
        
        return response


class APIService:
    """
    API Service that manages all API routers and handles requests
    
    This class serves as the main entry point for API requests,
    routing them to the appropriate handler based on the path and method.
    """
    
    def __init__(self):
        """Initialize the API service"""
        # Create routers
        self.auth_router = AuthRouter()
        self.user_router = UserRouter()
        self.data_router = DataRouter()
        self.project_router = ProjectRouter()
        self.do_router = DurableObjectRouter()
        
        # Combine all routers
        self.routers = [
            self.auth_router,
            self.user_router,
            self.data_router,
            self.project_router,
            self.do_router
        ]
    
    async def handle_request(
        self,
        path: str,
        method: str,
        data: Dict[str, Any],
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle an API request
        
        Args:
            path: Request path
            method: HTTP method
            data: Request data
            auth_token: Optional authentication token
            
        Returns:
            API response
        """
        # Find the handler for this route
        handler_config = None
        for router in self.routers:
            handler_config = router.get_handler(path, method)
            if handler_config:
                break
        
        if not handler_config:
            return {"error": f"Route not found: {method} {path}", "status_code": 404}
        
        # Check authentication if required
        user = None
        if handler_config["auth_required"]:
            if not auth_token:
                return {"error": "Authentication required", "status_code": 401}
            
            # Verify the token
            auth_objects = await list_durable_objects(object_type="AuthenticationDO")
            if not auth_objects:
                return {"error": "Authentication service unavailable", "status_code": 503}
            
            auth_id = auth_objects[0]["id"]
            auth_result = await send_request_to_object(
                object_id=auth_id,
                action="handle_verify_token",
                data={"token": auth_token}
            )
            
            if "error" in auth_result:
                return {"error": auth_result["error"], "status_code": 401}
            
            user = auth_result["payload"]
        
        # Call the handler
        handler = handler_config["handler"]
        try:
            if handler_config["auth_required"]:
                response = await handler(data, user)
            else:
                response = await handler(data)
            
            # Add status code if not present
            if "status_code" not in response:
                response["status_code"] = 200
            
            return response
        except Exception as e:
            logger.error(f"Error handling request {method} {path}: {str(e)}")
            return {"error": f"Internal server error: {str(e)}", "status_code": 500}


# Create a singleton API service instance
api_service = APIService()


async def handle_api_request(
    path: str,
    method: str,
    data: Dict[str, Any],
    auth_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle an API request
    
    This is the main entry point for API requests.
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data
        auth_token: Optional authentication token
        
    Returns:
        API response
    """
    return await api_service.handle_request(path, method, data, auth_token)
"""