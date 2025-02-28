#!/usr/bin/env python3
"""
Test script for the Data Service Durable Object.

This script demonstrates the basic functionality of the Data Service.
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

# Import the Data Service
from services.data_service import DataService


def main() -> None:
    """
    Main entry point for the Data Service test script.
    """
    logger.info("Starting Data Service test")
    
    # Create a Data Service instance with test configuration
    config = {
        "max_connections": 50,
        "timeout_seconds": 60
    }
    data_service = DataService(config)
    
    # For testing purposes, we'll use a fixed session ID
    # In a real scenario, this would come from the User Service
    test_session_id = "test-session-123"
    
    # Test data creation
    logger.info("Testing data creation")
    create_result = data_service.create_data_item(
        session_id=test_session_id,
        data_type="note",
        content={
            "title": "Test Note",
            "body": "This is a test note for the Data Service.",
            "tags": ["test", "note", "data"]
        }
    )
    logger.info(f"Create data result: {json.dumps(create_result, indent=2)}")
    
    # Store the data ID for later use
    data_id = create_result.get("id")
    
    if data_id:
        # Test data retrieval
        logger.info("Testing data retrieval")
        get_result = data_service.get_data_item(
            session_id=test_session_id,
            data_id=data_id
        )
        logger.info(f"Get data result: {json.dumps(get_result, indent=2)}")
        
        # Test data update
        logger.info("Testing data update")
        update_result = data_service.update_data_item(
            session_id=test_session_id,
            data_id=data_id,
            content={
                "title": "Updated Test Note",
                "body": "This note has been updated for testing.",
                "tags": ["test", "note", "updated"]
            }
        )
        logger.info(f"Update data result: {json.dumps(update_result, indent=2)}")
        
        # Verify the update
        logger.info("Verifying data update")
        get_updated_result = data_service.get_data_item(
            session_id=test_session_id,
            data_id=data_id
        )
        logger.info(f"Get updated data result: {json.dumps(get_updated_result, indent=2)}")
        
        # Test data listing
        logger.info("Testing data listing")
        list_result = data_service.list_data_items(
            session_id=test_session_id,
            data_type="note"
        )
        logger.info(f"List data result: {json.dumps(list_result, indent=2)}")
        
        # Test data deletion
        logger.info("Testing data deletion")
        delete_result = data_service.delete_data_item(
            session_id=test_session_id,
            data_id=data_id
        )
        logger.info(f"Delete data result: {json.dumps(delete_result, indent=2)}")
        
        # Verify the deletion
        logger.info("Verifying data deletion")
        get_deleted_result = data_service.get_data_item(
            session_id=test_session_id,
            data_id=data_id
        )
        logger.info(f"Get deleted data result: {json.dumps(get_deleted_result, indent=2)}")
    
    logger.info("Data Service test completed")


if __name__ == "__main__":
    main()
