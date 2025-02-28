"""
Data Service Durable Object for AIDevOS.

This module provides data storage and retrieval functionality.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.services.data_service")


class DataService:
    """
    Data Service Durable Object for data storage and retrieval.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Data Service.
        
        Args:
            config: Configuration parameters for the service
        """
        self.service_id = str(uuid.uuid4())
        self.config = config
        self.data_store = {}
        self.user_service = None  # This would be injected by the DO framework
        
        logger.info(f"Initializing Data Service {self.service_id}")
        logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    
    def set_user_service(self, user_service: Any) -> None:
        """
        Set the user service dependency.
        
        Args:
            user_service: User service instance
        """
        self.user_service = user_service
        logger.info("User service dependency injected")
    
    def create_data_item(self, session_id: str, data_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new data item.
        
        Args:
            session_id: Session ID for authentication
            data_type: Type of data to store
            content: Data content to store
            
        Returns:
            Dictionary containing the created data item information
        """
        # Validate session
        if self.user_service:
            session_result = self.user_service.validate_session(session_id)
            if not session_result.get("valid", False):
                logger.warning(f"Data creation failed: {session_result.get('error', 'Invalid session')}")
                return {"error": session_result.get("error", "Invalid session")}
            
            user_id = session_result["user_id"]
        else:
            # For testing without user service
            user_id = "test_user"
        
        # Create data item
        data_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        data_item = {
            "id": data_id,
            "type": data_type,
            "content": content,
            "owner_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Store data item
        self.data_store[data_id] = data_item
        
        logger.info(f"Created data item {data_id} of type {data_type}")
        return {
            "id": data_id,
            "type": data_type,
            "created_at": timestamp,
            "updated_at": timestamp
        }
    
    def get_data_item(self, session_id: str, data_id: str) -> Dict[str, Any]:
        """
        Retrieve a data item by ID.
        
        Args:
            session_id: Session ID for authentication
            data_id: ID of the data item to retrieve
            
        Returns:
            Dictionary containing the data item
        """
        # Validate session
        if self.user_service:
            session_result = self.user_service.validate_session(session_id)
            if not session_result.get("valid", False):
                logger.warning(f"Data retrieval failed: {session_result.get('error', 'Invalid session')}")
                return {"error": session_result.get("error", "Invalid session")}
            
            user_id = session_result["user_id"]
        else:
            # For testing without user service
            user_id = "test_user"
        
        # Retrieve data item
        if data_id not in self.data_store:
            logger.warning(f"Data item {data_id} not found")
            return {"error": "Data item not found"}
        
        data_item = self.data_store[data_id]
        
        # Check ownership
        if data_item["owner_id"] != user_id:
            logger.warning(f"Access denied: User {user_id} does not own data item {data_id}")
            return {"error": "Access denied"}
        
        logger.info(f"Retrieved data item {data_id}")
        return data_item
    
    def update_data_item(self, session_id: str, data_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a data item.
        
        Args:
            session_id: Session ID for authentication
            data_id: ID of the data item to update
            content: New data content
            
        Returns:
            Dictionary containing the updated data item information
        """
        # Validate session
        if self.user_service:
            session_result = self.user_service.validate_session(session_id)
            if not session_result.get("valid", False):
                logger.warning(f"Data update failed: {session_result.get('error', 'Invalid session')}")
                return {"error": session_result.get("error", "Invalid session")}
            
            user_id = session_result["user_id"]
        else:
            # For testing without user service
            user_id = "test_user"
        
        # Check if data item exists
        if data_id not in self.data_store:
            logger.warning(f"Data item {data_id} not found")
            return {"error": "Data item not found"}
        
        data_item = self.data_store[data_id]
        
        # Check ownership
        if data_item["owner_id"] != user_id:
            logger.warning(f"Access denied: User {user_id} does not own data item {data_id}")
            return {"error": "Access denied"}
        
        # Update data item
        data_item["content"] = content
        data_item["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated data item {data_id}")
        return {
            "id": data_id,
            "type": data_item["type"],
            "updated_at": data_item["updated_at"]
        }
    
    def delete_data_item(self, session_id: str, data_id: str) -> Dict[str, Any]:
        """
        Delete a data item.
        
        Args:
            session_id: Session ID for authentication
            data_id: ID of the data item to delete
            
        Returns:
            Dictionary containing the deletion result
        """
        # Validate session
        if self.user_service:
            session_result = self.user_service.validate_session(session_id)
            if not session_result.get("valid", False):
                logger.warning(f"Data deletion failed: {session_result.get('error', 'Invalid session')}")
                return {"error": session_result.get("error", "Invalid session")}
            
            user_id = session_result["user_id"]
        else:
            # For testing without user service
            user_id = "test_user"
        
        # Check if data item exists
        if data_id not in self.data_store:
            logger.warning(f"Data item {data_id} not found")
            return {"error": "Data item not found"}
        
        data_item = self.data_store[data_id]
        
        # Check ownership
        if data_item["owner_id"] != user_id:
            logger.warning(f"Access denied: User {user_id} does not own data item {data_id}")
            return {"error": "Access denied"}
        
        # Delete data item
        del self.data_store[data_id]
        
        logger.info(f"Deleted data item {data_id}")
        return {"success": True}
    
    def list_data_items(self, session_id: str, data_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List data items owned by the user.
        
        Args:
            session_id: Session ID for authentication
            data_type: Optional type filter
            
        Returns:
            Dictionary containing the list of data items
        """
        # Validate session
        if self.user_service:
            session_result = self.user_service.validate_session(session_id)
            if not session_result.get("valid", False):
                logger.warning(f"Data listing failed: {session_result.get('error', 'Invalid session')}")
                return {"error": session_result.get("error", "Invalid session")}
            
            user_id = session_result["user_id"]
        else:
            # For testing without user service
            user_id = "test_user"
        
        # Filter data items by owner and type
        items = []
        for item_id, item in self.data_store.items():
            if item["owner_id"] == user_id:
                if data_type is None or item["type"] == data_type:
                    # Return item without content for listing
                    items.append({
                        "id": item["id"],
                        "type": item["type"],
                        "created_at": item["created_at"],
                        "updated_at": item["updated_at"]
                    })
        
        logger.info(f"Listed {len(items)} data items for user {user_id}")
        return {"items": items}


# This function would be called when the Durable Object is deployed
def create_service(config: Dict[str, Any]) -> DataService:
    """
    Create a new instance of the Data Service.
    
    Args:
        config: Configuration parameters for the service
        
    Returns:
        Initialized Data Service instance
    """
    return DataService(config)
