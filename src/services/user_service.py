"""
User Service Durable Object for AIDevOS.

This module provides user authentication and management functionality.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.services.user_service")


class UserService:
    """
    User Service Durable Object for user authentication and management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the User Service.
        
        Args:
            config: Configuration parameters for the service
        """
        self.service_id = str(uuid.uuid4())
        self.config = config
        self.users = {}
        self.sessions = {}
        
        logger.info(f"Initializing User Service {self.service_id}")
        logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    
    def create_user(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: Username for the new user
            password: Password for the new user
            email: Email address for the new user
            
        Returns:
            Dictionary containing user information
        """
        if username in self.users:
            logger.warning(f"User {username} already exists")
            return {"error": "User already exists"}
        
        # In a real implementation, we would hash the password
        user_id = str(uuid.uuid4())
        self.users[username] = {
            "id": user_id,
            "username": username,
            "password": password,  # This would be hashed in a real implementation
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None
        }
        
        logger.info(f"Created user {username} with ID {user_id}")
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "created_at": self.users[username]["created_at"]
        }
    
    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user.
        
        Args:
            username: Username of the user to authenticate
            password: Password to verify
            
        Returns:
            Dictionary containing authentication result and session token if successful
        """
        if username not in self.users:
            logger.warning(f"Authentication failed: User {username} not found")
            return {"error": "Invalid username or password"}
        
        user = self.users[username]
        if user["password"] != password:  # This would use a proper comparison in a real implementation
            logger.warning(f"Authentication failed: Invalid password for user {username}")
            return {"error": "Invalid username or password"}
        
        # Create a session
        session_id = str(uuid.uuid4())
        expiration = datetime.utcnow() + timedelta(hours=24)
        
        self.sessions[session_id] = {
            "user_id": user["id"],
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiration.isoformat()
        }
        
        # Update last login time
        self.users[username]["last_login"] = datetime.utcnow().isoformat()
        
        logger.info(f"User {username} authenticated successfully")
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user["id"],
            "username": username,
            "expires_at": expiration.isoformat()
        }
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            Dictionary containing user information
        """
        for username, user in self.users.items():
            if user["id"] == user_id:
                # Return user info without password
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"]
                }
        
        logger.warning(f"User with ID {user_id} not found")
        return {"error": "User not found"}
    
    def validate_session(self, session_id: str) -> Dict[str, Any]:
        """
        Validate a session.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            Dictionary containing validation result and user information if valid
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return {"valid": False, "error": "Invalid session"}
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.utcnow() > expires_at:
            logger.warning(f"Session {session_id} has expired")
            # Clean up expired session
            del self.sessions[session_id]
            return {"valid": False, "error": "Session expired"}
        
        logger.info(f"Session {session_id} is valid")
        return {
            "valid": True,
            "user_id": session["user_id"],
            "username": session["username"]
        }
    
    def logout(self, session_id: str) -> Dict[str, Any]:
        """
        Log out a user by invalidating their session.
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            Dictionary containing logout result
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} invalidated")
            return {"success": True}
        
        logger.warning(f"Logout failed: Session {session_id} not found")
        return {"success": False, "error": "Session not found"}


# This function would be called when the Durable Object is deployed
def create_service(config: Dict[str, Any]) -> UserService:
    """
    Create a new instance of the User Service.
    
    Args:
        config: Configuration parameters for the service
        
    Returns:
        Initialized User Service instance
    """
    return UserService(config)
