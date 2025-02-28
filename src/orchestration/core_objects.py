"""
AIDevOS Core Durable Object Implementations

This module implements the core Durable Objects for the AIDevOS system,
including Authentication, User Management, Data Storage, and API Gateway objects.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import jwt

from .durable_objects import BaseDurableObject, registry
from .database import User, Project, APIKey, user_store, project_store, api_key_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key for JWT token generation and validation
# In production, this should be loaded from a secure environment variable
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
JWT_ALGORITHM = "HS256"


class AuthenticationDO(BaseDurableObject):
    """
    Authentication Durable Object
    
    Handles user authentication, authorization, and session management.
    """
    
    async def handle_login(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle login request
        
        Args:
            data: Login data including username and password
            metadata: Optional request metadata
            
        Returns:
            Authentication response with tokens or error
        """
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return {"error": "Username and password are required"}
        
        # Find the user by username
        users = await user_store.list(lambda u: u.username == username)
        if not users:
            return {"error": "Invalid username or password"}
        
        user = users[0]
        
        # Verify password
        password_hash = self._hash_password(password)
        if user.password_hash != password_hash:
            return {"error": "Invalid username or password"}
        
        # Generate tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        
        # Update last login time
        user.last_login = datetime.utcnow().isoformat()
        await user_store.update(user.id, user)
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": user.roles,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
    
    async def handle_register(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle user registration
        
        Args:
            data: Registration data
            metadata: Optional request metadata
            
        Returns:
            Registration response
        """
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        
        if not username or not email or not password:
            return {"error": "Username, email, and password are required"}
        
        # Check if username or email already exists
        existing_users = await user_store.list(
            lambda u: u.username == username or u.email == email
        )
        
        if existing_users:
            return {"error": "Username or email already exists"}
        
        # Create a new user
        password_hash = self._hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )
        
        await user_store.create(new_user)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": new_user.id
        }
    
    async def handle_refresh_token(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle token refresh
        
        Args:
            data: Refresh token data
            metadata: Optional request metadata
            
        Returns:
            New access token or error
        """
        refresh_token = data.get("refresh_token")
        
        if not refresh_token:
            return {"error": "Refresh token is required"}
        
        try:
            # Verify the refresh token
            payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            
            # Check if the token type is refresh
            if payload.get("type") != "refresh":
                return {"error": "Invalid token type"}
            
            # Get the user
            user = await user_store.read(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Generate a new access token
            access_token = self._generate_access_token(user)
            
            return {
                "success": True,
                "access_token": access_token
            }
        except jwt.ExpiredSignatureError:
            return {"error": "Refresh token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid refresh token"}
    
    async def handle_verify_token(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verify a token
        
        Args:
            data: Token data
            metadata: Optional request metadata
            
        Returns:
            Token verification result
        """
        token = data.get("token")
        
        if not token:
            return {"error": "Token is required"}
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return {
                "success": True,
                "payload": payload
            }
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}
    
    async def handle_logout(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle logout request
        
        In a production system, this would invalidate the token.
        For now, we just acknowledge the logout.
        
        Args:
            data: Logout data
            metadata: Optional request metadata
            
        Returns:
            Logout result
        """
        # In a full implementation, we would invalidate the token
        return {"success": True, "message": "Logged out successfully"}
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256
        
        In a production system, use a more secure hashing algorithm like bcrypt.
        
        Args:
            password: The password to hash
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_access_token(self, user: User) -> str:
        """
        Generate an access token for a user
        
        Args:
            user: The user to generate a token for
            
        Returns:
            JWT access token
        """
        expires = datetime.utcnow() + timedelta(minutes=30)
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "type": "access",
            "exp": expires
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    def _generate_refresh_token(self, user: User) -> str:
        """
        Generate a refresh token for a user
        
        Args:
            user: The user to generate a token for
            
        Returns:
            JWT refresh token
        """
        expires = datetime.utcnow() + timedelta(days=7)
        payload = {
            "sub": user.id,
            "type": "refresh",
            "exp": expires
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


class UserManagementDO(BaseDurableObject):
    """
    User Management Durable Object
    
    Handles user profile management, user settings, and user-related operations.
    """
    
    async def handle_get_user(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a user by ID
        
        Args:
            data: Request data with user ID
            metadata: Optional request metadata
            
        Returns:
            User data or error
        """
        user_id = data.get("user_id")
        if not user_id:
            return {"error": "User ID is required"}
        
        user = await user_store.read(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Return user data without sensitive information
        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": user.roles,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at,
                "last_login": user.last_login
            }
        }
    
    async def handle_update_user(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update a user's profile
        
        Args:
            data: Update data with user ID and fields to update
            metadata: Optional request metadata
            
        Returns:
            Update result or error
        """
        user_id = data.get("user_id")
        updates = data.get("updates", {})
        
        if not user_id or not updates:
            return {"error": "User ID and updates are required"}
        
        user = await user_store.read(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Update allowed fields
        allowed_fields = ["first_name", "last_name", "email", "settings"]
        for field in allowed_fields:
            if field in updates:
                setattr(user, field, updates[field])
        
        # Update password if provided
        if "password" in updates:
            user.password_hash = self._hash_password(updates["password"])
        
        # Save the updated user
        await user_store.update(user_id, user)
        
        return {
            "success": True,
            "message": "User updated successfully"
        }
    
    async def handle_list_users(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List users with optional filtering
        
        Args:
            data: Filter criteria
            metadata: Optional request metadata
            
        Returns:
            List of users or error
        """
        # Extract filter criteria
        role = data.get("role")
        active_only = data.get("active_only", True)
        
        # Define filter function
        def filter_func(user: User) -> bool:
            if active_only and not user.is_active:
                return False
            if role and role not in user.roles:
                return False
            return True
        
        # Get filtered users
        users = await user_store.list(filter_func)
        
        # Format user data for response
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": user.roles,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at,
                "is_active": user.is_active
            })
        
        return {
            "success": True,
            "users": user_list,
            "total": len(user_list)
        }
    
    async def handle_deactivate_user(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Deactivate a user
        
        Args:
            data: User ID to deactivate
            metadata: Optional request metadata
            
        Returns:
            Deactivation result or error
        """
        user_id = data.get("user_id")
        if not user_id:
            return {"error": "User ID is required"}
        
        user = await user_store.read(user_id)
        if not user:
            return {"error": "User not found"}
        
        user.is_active = False
        await user_store.update(user_id, user)
        
        return {
            "success": True,
            "message": "User deactivated successfully"
        }
    
    async def handle_activate_user(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Activate a user
        
        Args:
            data: User ID to activate
            metadata: Optional request metadata
            
        Returns:
            Activation result or error
        """
        user_id = data.get("user_id")
        if not user_id:
            return {"error": "User ID is required"}
        
        user = await user_store.read(user_id)
        if not user:
            return {"error": "User not found"}
        
        user.is_active = True
        await user_store.update(user_id, user)
        
        return {
            "success": True,
            "message": "User activated successfully"
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()


class DataStorageDO(BaseDurableObject):
    """
    Data Storage Durable Object
    
    Handles persistent data storage and retrieval for the system.
    """
    
    async def initialize(self) -> None:
        """Initialize the Data Storage object"""
        # Initialize collections map if not exists
        if "collections" not in self.state:
            self.state["collections"] = {}
        
        await super().initialize()
    
    async def handle_store_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store data in a collection
        
        Args:
            data: Store request with collection, id, and data
            metadata: Optional request metadata
            
        Returns:
            Storage result or error
        """
        collection = data.get("collection")
        item_id = data.get("id")
        item_data = data.get("data")
        
        if not collection or not item_data:
            return {"error": "Collection and data are required"}
        
        # Initialize collection if not exists
        if collection not in self.state["collections"]:
            self.state["collections"][collection] = {}
        
        # Generate ID if not provided
        if not item_id:
            item_id = str(time.time()) + "-" + str(hash(json.dumps(item_data, sort_keys=True)))
        
        # Store the data
        item_with_metadata = {
            "id": item_id,
            "data": item_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.state["collections"][collection][item_id] = item_with_metadata
        await self._save_state()
        
        return {
            "success": True,
            "id": item_id,
            "collection": collection
        }
    
    async def handle_retrieve_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve data from a collection
        
        Args:
            data: Retrieve request with collection and id
            metadata: Optional request metadata
            
        Returns:
            Retrieved data or error
        """
        collection = data.get("collection")
        item_id = data.get("id")
        
        if not collection or not item_id:
            return {"error": "Collection and ID are required"}
        
        # Check if collection exists
        if collection not in self.state["collections"]:
            return {"error": f"Collection '{collection}' not found"}
        
        # Check if item exists
        if item_id not in self.state["collections"][collection]:
            return {"error": f"Item '{item_id}' not found in collection '{collection}'"}
        
        # Return the item
        return {
            "success": True,
            "item": self.state["collections"][collection][item_id]
        }
    
    async def handle_update_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update data in a collection
        
        Args:
            data: Update request with collection, id, and data
            metadata: Optional request metadata
            
        Returns:
            Update result or error
        """
        collection = data.get("collection")
        item_id = data.get("id")
        item_data = data.get("data")
        
        if not collection or not item_id or not item_data:
            return {"error": "Collection, ID, and data are required"}
        
        # Check if collection exists
        if collection not in self.state["collections"]:
            return {"error": f"Collection '{collection}' not found"}
        
        # Check if item exists
        if item_id not in self.state["collections"][collection]:
            return {"error": f"Item '{item_id}' not found in collection '{collection}'"}
        
        # Update the item
        current_item = self.state["collections"][collection][item_id]
        current_item["data"].update(item_data)
        current_item["updated_at"] = datetime.utcnow().isoformat()
        
        await self._save_state()
        
        return {
            "success": True,
            "id": item_id,
            "collection": collection
        }
    
    async def handle_delete_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Delete data from a collection
        
        Args:
            data: Delete request with collection and id
            metadata: Optional request metadata
            
        Returns:
            Delete result or error
        """
        collection = data.get("collection")
        item_id = data.get("id")
        
        if not collection or not item_id:
            return {"error": "Collection and ID are required"}
        
        # Check if collection exists
        if collection not in self.state["collections"]:
            return {"error": f"Collection '{collection}' not found"}
        
        # Check if item exists
        if item_id not in self.state["collections"][collection]:
            return {"error": f"Item '{item_id}' not found in collection '{collection}'"}
        
        # Delete the item
        del self.state["collections"][collection][item_id]
        await self._save_state()
        
        return {
            "success": True,
            "message": f"Item '{item_id}' deleted from collection '{collection}'"
        }
    
    async def handle_query_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query data in a collection
        
        Args:
            data: Query request with collection and query criteria
            metadata: Optional request metadata
            
        Returns:
            Query results or error
        """
        collection = data.get("collection")
        query = data.get("query", {})
        limit = data.get("limit")
        skip = data.get("skip", 0)
        
        if not collection:
            return {"error": "Collection is required"}
        
        # Check if collection exists
        if collection not in self.state["collections"]:
            return {"error": f"Collection '{collection}' not found"}
        
        # Get all items in the collection
        items = list(self.state["collections"][collection].values())
        
        # Filter items based on query
        if query:
            filtered_items = []
            for item in items:
                match = True
                for key, value in query.items():
                    # Handle nested keys with dot notation
                    if "." in key:
                        parts = key.split(".")
                        item_value = item
                        for part in parts:
                            if isinstance(item_value, dict) and part in item_value:
                                item_value = item_value[part]
                            else:
                                item_value = None
                                break
                    else:
                        item_value = item["data"].get(key) if key in item["data"] else None
                    
                    # Simple equality match
                    if item_value != value:
                        match = False
                        break
                
                if match:
                    filtered_items.append(item)
            
            items = filtered_items
        
        # Apply pagination
        total = len(items)
        if skip:
            items = items[skip:]
        if limit:
            items = items[:limit]
        
        return {
            "success": True,
            "items": items,
            "total": total,
            "returned": len(items)
        }
    
    async def handle_list_collections(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all collections
        
        Args:
            data: Empty request data
            metadata: Optional request metadata
            
        Returns:
            List of collections
        """
        collections = []
        for collection_name, collection_data in self.state["collections"].items():
            collections.append({
                "name": collection_name,
                "item_count": len(collection_data)
            })
        
        return {
            "success": True,
            "collections": collections,
            "total": len(collections)
        }


class APIGatewayDO(BaseDurableObject):
    """
    API Gateway Durable Object
    
    Handles API requests, routing, and API key management.
    """
    
    async def initialize(self) -> None:
        """Initialize the API Gateway object"""
        # Initialize routes map if not exists
        if "routes" not in self.state:
            self.state["routes"] = {}
            
            # Add default routes
            self.state["routes"]["/auth"] = {
                "object_type": "AuthenticationDO",
                "actions": {
                    "login": "handle_login",
                    "register": "handle_register",
                    "refresh_token": "handle_refresh_token",
                    "verify_token": "handle_verify_token",
                    "logout": "handle_logout"
                }
            }
            
            self.state["routes"]["/users"] = {
                "object_type": "UserManagementDO",
                "actions": {
                    "get_user": "handle_get_user",
                    "update_user": "handle_update_user",
                    "list_users": "handle_list_users",
                    "deactivate_user": "handle_deactivate_user",
                    "activate_user": "handle_activate_user"
                }
            }
            
            self.state["routes"]["/data"] = {
                "object_type": "DataStorageDO",
                "actions": {
                    "store_data": "handle_store_data",
                    "retrieve_data": "handle_retrieve_data",
                    "update_data": "handle_update_data",
                    "delete_data": "handle_delete_data",
                    "query_data": "handle_query_data",
                    "list_collections": "handle_list_collections"
                }
            }
            
            self.state["routes"]["/api"] = {
                "object_type": "APIGatewayDO",
                "actions": {
                    "create_api_key": "handle_create_api_key",
                    "revoke_api_key": "handle_revoke_api_key",
                    "verify_api_key": "handle_verify_api_key",
                    "list_api_keys": "handle_list_api_keys",
                    "add_route": "handle_add_route",
                    "remove_route": "handle_remove_route",
                    "list_routes": "handle_list_routes"
                }
            }
        
        await super().initialize()
    
    async def handle_process_request(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an API request
        
        Args:
            data: Request data with path, action, and payload
            metadata: Optional request metadata
            
        Returns:
            Response from the appropriate handler
        """
        path = data.get("path")
        action = data.get("action")
        payload = data.get("payload", {})
        auth_token = data.get("auth_token")
        api_key = data.get("api_key")
        
        if not path or not action:
            return {"error": "Path and action are required"}
        
        # Find the route
        route = self.state["routes"].get(path)
        if not route:
            return {"error": f"Route not found: {path}"}
        
        # Check if the action is supported
        if action not in route["actions"]:
            return {"error": f"Action not supported: {action}"}
        
        # Handle authentication
        if auth_token:
            # Verify the token
            auth_result = await self._verify_token(auth_token)
            if "error" in auth_result:
                return auth_result
            
            # Add user info to the payload for the handler
            payload["_user"] = auth_result["payload"]
        elif api_key:
            # Verify the API key
            api_key_result = await self._verify_api_key(api_key, path, action)
            if "error" in api_key_result:
                return api_key_result
            
            # Add API key info to the payload for the handler
            payload["_api_key"] = api_key_result["api_key"]
        else:
            # Check if this is a public route/action
            public_routes = ["/auth/login", "/auth/register", "/auth/refresh_token"]
            if f"{path}/{action}" not in public_routes:
                return {"error": "Authentication required"}
        
        # Get the target object type and action
        object_type = route["object_type"]
        handler_action = route["actions"][action]
        
        # Create a Durable Object for the target type
        # In a real implementation, this would use a registry to get an existing object
        # or create a new one. For now, we'll simulate the request.
        return await self._simulate_object_request(object_type, handler_action, payload)
    
    async def handle_create_api_key(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new API key
        
        Args:
            data: Request data with user_id, name, and permissions
            metadata: Optional request metadata
            
        Returns:
            Created API key or error
        """
        user_id = data.get("user_id")
        project_id = data.get("project_id")
        name = data.get("name", "API Key")
        permissions = data.get("permissions", ["read"])
        expires_days = data.get("expires_days")
        
        if not user_id:
            return {"error": "User ID is required"}
        
        # Generate a secure API key
        api_key_value = self._generate_api_key()
        
        # Calculate expiration if provided
        expires_at = None
        if expires_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_days)).isoformat()
        
        # Store the API key
        api_key = APIKey(
            key=api_key_value,
            user_id=user_id,
            project_id=project_id,
            permissions=permissions,
            name=name,
            expires_at=expires_at
        )
        
        await api_key_store.create(api_key)
        
        return {
            "success": True,
            "api_key": {
                "id": api_key.id,
                "key": api_key_value,  # This should only be shown once
                "name": api_key.name,
                "permissions": api_key.permissions,
                "expires_at": api_key.expires_at
            }
        }
    
    async def handle_revoke_api_key(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Revoke an API key
        
        Args:
            data: Request data with api_key_id
            metadata: Optional request metadata
            
        Returns:
            Revocation result or error
        """
        api_key_id = data.get("api_key_id")
        
        if not api_key_id:
            return {"error": "API key ID is required"}
        
        # Get the API key
        api_key = await api_key_store.read(api_key_id)
        if not api_key:
            return {"error": "API key not found"}
        
        # Deactivate the API key
        api_key.is_active = False
        await api_key_store.update(api_key_id, api_key)
        
        return {
            "success": True,
            "message": "API key revoked successfully"
        }
    
    async def handle_verify_api_key(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verify an API key
        
        Args:
            data: Request data with api_key, path, and action
            metadata: Optional request metadata
            
        Returns:
            Verification result or error
        """
        api_key = data.get("api_key")
        path = data.get("path")
        action = data.get("action")
        
        if not api_key:
            return {"error": "API key is required"}
        
        return await self._verify_api_key(api_key, path, action)
    
    async def handle_list_api_keys(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List API keys for a user
        
        Args:
            data: Request data with user_id
            metadata: Optional request metadata
            
        Returns:
            List of API keys or error
        """
        user_id = data.get("user_id")
        
        if not user_id:
            return {"error": "User ID is required"}
        
        # Get API keys for the user
        api_keys = await api_key_store.list(lambda k: k.user_id == user_id and k.is_active)
        
        # Format API keys for response (excluding the actual key)
        api_key_list = []
        for key in api_keys:
            api_key_list.append({
                "id": key.id,
                "name": key.name,
                "permissions": key.permissions,
                "created_at": key.created_at,
                "expires_at": key.expires_at,
                "last_used": key.last_used,
                "project_id": key.project_id
            })
        
        return {
            "success": True,
            "api_keys": api_key_list,
            "total": len(api_key_list)
        }
    
    async def handle_add_route(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new API route
        
        Args:
            data: Request data with path, object_type, and actions
            metadata: Optional request metadata
            
        Returns:
            Route addition result or error
        """
        path = data.get("path")
        object_type = data.get("object_type")
        actions = data.get("actions", {})
        
        if not path or not object_type or not actions:
            return {"error": "Path, object type, and actions are required"}
        
        # Add the route
        self.state["routes"][path] = {
            "object_type": object_type,
            "actions": actions
        }
        
        await self._save_state()
        
        return {
            "success": True,
            "message": f"Route '{path}' added successfully"
        }
    
    async def handle_remove_route(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Remove an API route
        
        Args:
            data: Request data with path
            metadata: Optional request metadata
            
        Returns:
            Route removal result or error
        """
        path = data.get("path")
        
        if not path:
            return {"error": "Path is required"}
        
        # Check if the route exists
        if path not in self.state["routes"]:
            return {"error": f"Route not found: {path}"}
        
        # Remove the route
        del self.state["routes"][path]
        await self._save_state()
        
        return {
            "success": True,
            "message": f"Route '{path}' removed successfully"
        }
    
    async def handle_list_routes(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all API routes
        
        Args:
            data: Empty request data
            metadata: Optional request metadata
            
        Returns:
            List of routes
        """
        routes = []
        for path, route_data in self.state["routes"].items():
            routes.append({
                "path": path,
                "object_type": route_data["object_type"],
                "actions": list(route_data["actions"].keys())
            })
        
        return {
            "success": True,
            "routes": routes,
            "total": len(routes)
        }
    
    async def _verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify an authentication token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Verification result or error
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return {
                "success": True,
                "payload": payload
            }
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}
    
    async def _verify_api_key(
        self,
        api_key: str,
        path: Optional[str] = None,
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify an API key
        
        Args:
            api_key: API key to verify
            path: Optional path to check access for
            action: Optional action to check access for
            
        Returns:
            Verification result or error
        """
        # Find the API key
        api_keys = await api_key_store.list(lambda k: k.key == api_key and k.is_active)
        if not api_keys:
            return {"error": "Invalid API key"}
        
        key = api_keys[0]
        
        # Check if expired
        if key.expires_at:
            expires = datetime.fromisoformat(key.expires_at)
            if expires < datetime.utcnow():
                return {"error": "API key expired"}
        
        # Check permissions if path and action are provided
        if path and action:
            # Here we would implement more sophisticated permission checking
            # For now, we'll just check if the key has read/write permissions
            if "read" not in key.permissions and action.startswith("get_"):
                return {"error": "Insufficient permissions for this action"}
            
            if "write" not in key.permissions and not action.startswith("get_"):
                return {"error": "Insufficient permissions for this action"}
        
        # Update last used time
        key.last_used = datetime.utcnow().isoformat()
        await api_key_store.update(key.id, key)
        
        return {
            "success": True,
            "api_key": {
                "id": key.id,
                "user_id": key.user_id,
                "permissions": key.permissions,
                "project_id": key.project_id
            }
        }
    
    def _generate_api_key(self) -> str:
        """
        Generate a new API key
        
        Returns:
            Secure API key string
        """
        # In production, use a more secure method
        key = hashlib.sha256(os.urandom(32)).hexdigest()
        return f"aido_{key[:32]}"
    
    async def _simulate_object_request(
        self,
        object_type: str,
        action: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate a request to another Durable Object
        
        In a real implementation, this would use the registry to get
        an existing object or create a new one. For now, we'll simulate
        the request for demonstration purposes.
        
        Args:
            object_type: Type of the target object
            action: Action to perform
            data: Data for the action
            
        Returns:
            Response from the object
        """
        # For demonstration purposes, we'll just return a simulated response
        return {
            "success": True,
            "message": f"Request to {object_type}.{action} simulated",
            "data": data
        }


# Register Durable Object types with the registry
registry.register_object_type("AuthenticationDO", AuthenticationDO)
registry.register_object_type("UserManagementDO", UserManagementDO)
registry.register_object_type("DataStorageDO", DataStorageDO)
registry.register_object_type("APIGatewayDO", APIGatewayDO)
"""