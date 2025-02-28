"""
AIDevOS Authentication Module
This module handles user authentication and authorization for the AIDevOS system.
"""

import os
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

# Secret key for JWT token generation and validation
# In production, this should be loaded from a secure environment variable
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthenticationManager:
    """Manages authentication for the AIDevOS system"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token with the provided data
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token
        
        Args:
            token: The JWT token to verify
            
        Returns:
            The decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None


class AuthorizationManager:
    """Manages authorization for the AIDevOS system"""
    
    @staticmethod
    def has_permission(user_roles: list, required_roles: list) -> bool:
        """
        Check if a user has the required roles
        
        Args:
            user_roles: List of roles assigned to the user
            required_roles: List of roles required for the operation
            
        Returns:
            True if the user has at least one of the required roles, False otherwise
        """
        return any(role in required_roles for role in user_roles)