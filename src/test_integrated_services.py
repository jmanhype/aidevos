#!/usr/bin/env python3
"""
Integrated test script for User Service and Data Service interaction.

This script demonstrates how the User Service and Data Service can work together
in the AIDevOS Durable Objects architecture.
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

# Import the services
from services.user_service import UserService
from services.data_service import DataService


def main() -> None:
    """
    Main entry point for the integrated services test script.
    """
    logger.info("Starting integrated services test")
    
    # Create service instances with test configurations
    user_service = UserService({
        "max_connections": 100,
        "timeout_seconds": 30
    })
    
    data_service = DataService({
        "max_connections": 50,
        "timeout_seconds": 60
    })
    
    # Set up the dependency injection
    data_service.set_user_service(user_service)
    
    # Create a test user
    logger.info("Creating test user")
    user_result = user_service.create_user(
        username="integrated_test_user",
        password="secure_password_123",
        email="test@example.com"
    )
    logger.info(f"User creation result: {json.dumps(user_result, indent=2)}")
    
    # Authenticate the user to get a session
    logger.info("Authenticating user")
    auth_result = user_service.authenticate(
        username="integrated_test_user",
        password="secure_password_123"
    )
    logger.info(f"Authentication result: {json.dumps(auth_result, indent=2)}")
    
    # Extract session ID and user ID for later use
    session_id = auth_result.get("session_id")
    user_id = auth_result.get("user_id")
    
    if not session_id:
        logger.error("Failed to get session ID, aborting test")
        return
    
    # Create data items using the authenticated session
    logger.info("Creating data items with authenticated session")
    data_items = []
    
    # Create multiple data items of different types
    for i in range(3):
        data_type = "note" if i % 2 == 0 else "document"
        create_result = data_service.create_data_item(
            session_id=session_id,
            data_type=data_type,
            content={
                "title": f"Test {data_type.capitalize()} {i+1}",
                "body": f"This is test content for {data_type} {i+1}",
                "tags": ["test", data_type, f"item-{i+1}"]
            }
        )
        logger.info(f"Created {data_type}: {json.dumps(create_result, indent=2)}")
        data_items.append(create_result)
    
    # List all data items
    logger.info("Listing all data items")
    all_items = data_service.list_data_items(session_id)
    logger.info(f"All items: {json.dumps(all_items, indent=2)}")
    
    # List only notes
    logger.info("Listing only notes")
    notes = data_service.list_data_items(session_id, data_type="note")
    logger.info(f"Notes: {json.dumps(notes, indent=2)}")
    
    # List only documents
    logger.info("Listing only documents")
    documents = data_service.list_data_items(session_id, data_type="document")
    logger.info(f"Documents: {json.dumps(documents, indent=2)}")
    
    # Update a data item
    if data_items and len(data_items) > 0:
        data_id = data_items[0].get("id")
        logger.info(f"Updating data item {data_id}")
        update_result = data_service.update_data_item(
            session_id=session_id,
            data_id=data_id,
            content={
                "title": "Updated Item",
                "body": "This item has been updated during the integrated test.",
                "tags": ["test", "updated", "integrated"]
            }
        )
        logger.info(f"Update result: {json.dumps(update_result, indent=2)}")
        
        # Verify the update
        get_result = data_service.get_data_item(session_id, data_id)
        logger.info(f"Updated item: {json.dumps(get_result, indent=2)}")
    
    # Test session invalidation
    logger.info("Testing session invalidation")
    logout_result = user_service.logout(session_id)
    logger.info(f"Logout result: {json.dumps(logout_result, indent=2)}")
    
    # Try to access data after logout (should fail)
    logger.info("Attempting to access data after logout (should fail)")
    if data_items and len(data_items) > 0:
        data_id = data_items[0].get("id")
        access_after_logout = data_service.get_data_item(session_id, data_id)
        logger.info(f"Access after logout: {json.dumps(access_after_logout, indent=2)}")
    
    logger.info("Integrated services test completed")


if __name__ == "__main__":
    main()
