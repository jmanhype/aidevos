"""
AIDevOS Orchestration Layer

This package implements the orchestration layer for AIDevOS, providing
the Durable Objects framework, API services, and database models.
"""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import key components to make them available at the package level
from .database import (
    Model, User, Project, DurableObject, APIKey, Task,
    DataStore, InMemoryDataStore,
    user_store, project_store, durable_object_store, api_key_store, task_store
)

from .durable_objects import (
    BaseDurableObject, DurableObjectRegistry, DurableObjectRouter, EventBus,
    create_durable_object, get_durable_object, update_durable_object,
    delete_durable_object, list_durable_objects, send_request_to_object,
    publish_event,
    registry, router, event_bus
)

from .core_objects import (
    AuthenticationDO, UserManagementDO, DataStorageDO, APIGatewayDO
)

from .api_service import (
    APIRouter, AuthRouter, UserRouter, DataRouter, ProjectRouter, DurableObjectRouter,
    APIService, handle_api_request,
    api_service
)

from .openapi_spec import (
    generate_openapi_spec, save_openapi_spec
)


async def initialize_orchestration_layer(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the orchestration layer with optional configuration
    
    Args:
        config: Optional configuration dict
    """
    logger.info("Initializing AIDevOS orchestration layer")
    
    # Apply configuration if provided
    if config:
        logger.info(f"Applying configuration: {config}")
        # TODO: Apply configuration settings
    
    # Create initial system objects if needed
    auth_objects = await list_durable_objects(object_type="AuthenticationDO")
    if not auth_objects:
        logger.info("Creating system Authentication object")
        await create_durable_object(
            type_name="AuthenticationDO",
            project_id="system",
            name="System Authentication Service"
        )
    
    user_mgmt_objects = await list_durable_objects(object_type="UserManagementDO")
    if not user_mgmt_objects:
        logger.info("Creating system User Management object")
        await create_durable_object(
            type_name="UserManagementDO",
            project_id="system",
            name="System User Management Service"
        )
    
    data_storage_objects = await list_durable_objects(object_type="DataStorageDO")
    if not data_storage_objects:
        logger.info("Creating system Data Storage object")
        await create_durable_object(
            type_name="DataStorageDO",
            project_id="system",
            name="System Data Storage Service"
        )
    
    api_gateway_objects = await list_durable_objects(object_type="APIGatewayDO")
    if not api_gateway_objects:
        logger.info("Creating system API Gateway object")
        await create_durable_object(
            type_name="APIGatewayDO",
            project_id="system",
            name="System API Gateway Service"
        )
    
    logger.info("AIDevOS orchestration layer initialized successfully")


__all__ = [
    # Database models
    'Model', 'User', 'Project', 'DurableObject', 'APIKey', 'Task',
    'DataStore', 'InMemoryDataStore',
    'user_store', 'project_store', 'durable_object_store', 'api_key_store', 'task_store',
    
    # Durable Objects framework
    'BaseDurableObject', 'DurableObjectRegistry', 'DurableObjectRouter', 'EventBus',
    'create_durable_object', 'get_durable_object', 'update_durable_object',
    'delete_durable_object', 'list_durable_objects', 'send_request_to_object',
    'publish_event',
    'registry', 'router', 'event_bus',
    
    # Core objects
    'AuthenticationDO', 'UserManagementDO', 'DataStorageDO', 'APIGatewayDO',
    
    # API service
    'APIRouter', 'AuthRouter', 'UserRouter', 'DataRouter', 'ProjectRouter', 'DurableObjectRouter',
    'APIService', 'handle_api_request',
    'api_service',
    
    # OpenAPI
    'generate_openapi_spec', 'save_openapi_spec',
    
    # Initialization
    'initialize_orchestration_layer'
]
"""