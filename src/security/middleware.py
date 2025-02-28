"""
AIDevOS Security Middleware
This module provides security middleware for protecting API endpoints and services.
"""

import os
import time
import hashlib
import json
from typing import Dict, List, Callable, Any, Optional
from functools import wraps

from .authentication import AuthenticationManager, AuthorizationManager


def authenticate_request(func: Callable) -> Callable:
    """
    Decorator to authenticate API requests using JWT tokens
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function that authenticates requests before processing
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract authorization header from the request
        # This assumes the first argument is the request object
        request = args[0]
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Unauthorized - Missing or invalid token"}, 401
        
        token = auth_header.split(" ")[1]
        payload = AuthenticationManager.verify_token(token)
        
        if not payload:
            return {"error": "Unauthorized - Invalid token"}, 401
        
        # Add the user data to the request object for later use
        request.user = payload
        
        return func(*args, **kwargs)
    
    return wrapper


def require_roles(required_roles: List[str]) -> Callable:
    """
    Decorator to enforce role-based access control
    
    Args:
        required_roles: List of roles allowed to access the endpoint
        
    Returns:
        Decorated function that checks user roles before processing
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This assumes authenticate_request has been applied first
            request = args[0]
            
            if not hasattr(request, "user"):
                return {"error": "Unauthorized - Authentication required"}, 401
            
            user_roles = request.user.get("roles", [])
            
            if not AuthorizationManager.has_permission(user_roles, required_roles):
                return {"error": "Forbidden - Insufficient permissions"}, 403
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def rate_limit(max_requests: int, window_seconds: int) -> Callable:
    """
    Decorator to implement rate limiting for API endpoints
    
    Args:
        max_requests: Maximum number of requests allowed within the window
        window_seconds: Time window in seconds
        
    Returns:
        Decorated function that enforces rate limits
    """
    # Store request counts by IP
    request_records: Dict[str, List[float]] = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract client IP from the request
            request = args[0]
            client_ip = request.remote_addr
            
            # Initialize request record for this IP if not exists
            if client_ip not in request_records:
                request_records[client_ip] = []
            
            # Get current time
            current_time = time.time()
            
            # Remove requests outside the window
            request_records[client_ip] = [
                timestamp for timestamp in request_records[client_ip]
                if current_time - timestamp < window_seconds
            ]
            
            # Check if rate limit exceeded
            if len(request_records[client_ip]) >= max_requests:
                return {"error": "Too many requests"}, 429
            
            # Add current request timestamp
            request_records[client_ip].append(current_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def csrf_protection(func: Callable) -> Callable:
    """
    Decorator to protect against CSRF attacks
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function that validates CSRF tokens
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        
        # Skip CSRF check for GET, HEAD, OPTIONS requests
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return func(*args, **kwargs)
        
        # For other methods, check CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        session_token = request.session.get("csrf_token")
        
        if not csrf_token or not session_token or csrf_token != session_token:
            return {"error": "CSRF token validation failed"}, 403
        
        return func(*args, **kwargs)
    
    return wrapper


def sanitize_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data to prevent injection attacks
    
    Args:
        input_data: The input data to sanitize
        
    Returns:
        Sanitized input data
    """
    sanitized_data = {}
    
    for key, value in input_data.items():
        if isinstance(value, str):
            # Basic sanitization - remove dangerous characters
            sanitized_value = value.replace("<", "&lt;").replace(">", "&gt;")
            sanitized_data[key] = sanitized_value
        elif isinstance(value, dict):
            sanitized_data[key] = sanitize_input(value)
        elif isinstance(value, list):
            sanitized_data[key] = [
                sanitize_input(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized_data[key] = value
    
    return sanitized_data