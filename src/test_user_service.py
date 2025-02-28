#!/usr/bin/env python3
"""
Test script for the User Service Durable Object.

This script demonstrates the basic functionality of the User Service.
"""

import json
import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("aidevos.test")

# Import the User Service
from services.user_service import UserService


def main() -> None:
    """
    Main entry point for the User Service test script.
    """
    logger.info("Starting User Service test")
    
    # Create a User Service instance with test configuration
    config = {
        "max_connections": 100,
        "timeout_seconds": 30
    }
    user_service = UserService(config)
    
    # Test user creation
    logger.info("Testing user creation")
    create_result = user_service.create_user(
        username="testuser",
        password="password123",
        email="testuser@example.com"
    )
    logger.info(f"Create user result: {json.dumps(create_result, indent=2)}")
    
    # Test authentication
    logger.info("Testing user authentication")
    auth_result = user_service.authenticate(
        username="testuser",
        password="password123"
    )
    logger.info(f"Authentication result: {json.dumps(auth_result, indent=2)}")
    
    # Store the session ID for later use
    session_id = auth_result.get("session_id")
    
    if session_id:
        # Test session validation
        logger.info("Testing session validation")
        validate_result = user_service.validate_session(session_id)
        logger.info(f"Session validation result: {json.dumps(validate_result, indent=2)}")
        
        # Test user retrieval
        logger.info("Testing user retrieval")
        user_id = auth_result.get("user_id")
        get_result = user_service.get_user(user_id)
        logger.info(f"Get user result: {json.dumps(get_result, indent=2)}")
        
        # Test logout
        logger.info("Testing user logout")
        logout_result = user_service.logout(session_id)
        logger.info(f"Logout result: {json.dumps(logout_result, indent=2)}")
        
        # Verify session is invalid after logout
        logger.info("Verifying session is invalid after logout")
        validate_after_logout = user_service.validate_session(session_id)
        logger.info(f"Session validation after logout: {json.dumps(validate_after_logout, indent=2)}")
    
    logger.info("User Service test completed")


if __name__ == "__main__":
    main()
