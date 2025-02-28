"""
Durable Objects Deployment Manager for AIDevOS.

This module provides functionality for deploying, updating, and managing
Durable Objects in the AIDevOS system.
"""

import argparse
import json
import logging
import os
import sys
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.do_deployer")


class DurableObjectDeployer:
    """
    Durable Objects deployment manager for AIDevOS.
    
    This class handles the deployment, updating, and management of
    Durable Objects in the AIDevOS system.
    """
    
    def __init__(
        self,
        registry_url: str = "http://localhost:8000/registry",
        auth_token: Optional[str] = None,
        config_path: str = "config/durable_objects.json",
    ):
        """
        Initialize the Durable Objects deployer.
        
        Args:
            registry_url: URL of the Durable Objects registry service
            auth_token: Authentication token for the registry service
            config_path: Path to the Durable Objects configuration file
        """
        self.registry_url = registry_url
        self.auth_token = auth_token or os.environ.get("AIDEVOS_REGISTRY_TOKEN")
        self.config_path = config_path
        self.deployment_id = str(uuid.uuid4())
        
        if not self.auth_token:
            logger.warning("No authentication token provided for registry service")
            
        logger.info(f"Initializing Durable Objects deployment {self.deployment_id}")
    
    def load_configuration(self) -> Dict[str, Any]:
        """
        Load Durable Objects configuration from the config file.
        
        Returns:
            Dictionary containing the Durable Objects configuration
        
        Raises:
            FileNotFoundError: If the configuration file is not found
            json.JSONDecodeError: If the configuration file is not valid JSON
        """
        logger.info(f"Loading Durable Objects configuration from {self.config_path}")
        
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                
            logger.info(f"Loaded configuration for {len(config.get('objects', []))} Durable Objects")
            return config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {self.config_path}")
            raise
    
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate the Durable Objects configuration.
        
        Args:
            config: Dictionary containing the Durable Objects configuration
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        logger.info("Validating Durable Objects configuration")
        
        # Check required keys
        if "objects" not in config:
            logger.error("Configuration is missing 'objects' key")
            return False
        
        # Check that each object has required fields
        for i, obj in enumerate(config["objects"]):
            if "name" not in obj:
                logger.error(f"Object at index {i} is missing 'name' field")
                return False
                
            if "version" not in obj:
                logger.error(f"Object '{obj.get('name', f'[{i}]')}' is missing 'version' field")
                return False
                
            if "code_path" not in obj:
                logger.error(f"Object '{obj.get('name', f'[{i}]')}' is missing 'code_path' field")
                return False
        
        logger.info("Configuration is valid")
        return True
    
    def add_durable_object(self, durable_object: Dict[str, Any]) -> bool:
        """
        Add a new Durable Object to the configuration.
        
        Args:
            durable_object: Dictionary containing the Durable Object configuration.
                Must contain 'name', 'version', and either 'code_path' or 'path' fields.
                
        Returns:
            True if the Durable Object was successfully added, False otherwise.
            
        Raises:
            FileNotFoundError: If the configuration file is not found
            json.JSONDecodeError: If the configuration file is not valid JSON
        """
        logger.info(f"Adding Durable Object: {durable_object.get('name', 'unnamed')}")
        
        # Validate required fields
        if "name" not in durable_object:
            logger.error("Durable Object configuration is missing 'name' field")
            return False
            
        if "version" not in durable_object:
            logger.error(f"Durable Object '{durable_object['name']}' is missing 'version' field")
            return False
            
        # Handle path/code_path field
        if "path" in durable_object and "code_path" not in durable_object:
            durable_object["code_path"] = durable_object["path"]
            
        if "code_path" not in durable_object:
            logger.error(f"Durable Object '{durable_object['name']}' is missing 'code_path' or 'path' field")
            return False
            
        # Load existing configuration
        try:
            config = self.load_configuration()
        except (FileNotFoundError, json.JSONDecodeError):
            # If the configuration file doesn't exist or is invalid, create a new one
            config = {"objects": []}
            
        # Check if the Durable Object already exists
        existing_object = None
        for i, obj in enumerate(config.get("objects", [])):
            if obj.get("name") == durable_object["name"]:
                existing_object = i
                break
                
        # Update existing or add new
        if existing_object is not None:
            logger.info(f"Updating existing Durable Object: {durable_object['name']}")
            config["objects"][existing_object] = durable_object
        else:
            logger.info(f"Adding new Durable Object: {durable_object['name']}")
            if "objects" not in config:
                config["objects"] = []
            config["objects"].append(durable_object)
            
        # Save configuration
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)
            
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Configuration updated with Durable Object: {durable_object['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def deploy_durable_objects(self, config: Dict[str, Any]) -> bool:
        """
        Deploy Durable Objects based on the configuration.
        
        Args:
            config: Dictionary containing the Durable Objects configuration
            
        Returns:
            True if all Durable Objects were deployed successfully, False otherwise
        """
        logger.info("Starting Durable Objects deployment")
        
        objects = config.get("objects", [])
        total_objects = len(objects)
        successful_deployments = 0
        
        for i, obj in enumerate(objects):
            obj_name = obj["name"]
            obj_version = obj["version"]
            
            logger.info(f"Deploying Durable Object {i+1}/{total_objects}: {obj_name} (v{obj_version})")
            
            try:
                # Check if the object already exists
                if self._object_exists(obj_name):
                    # Update existing object
                    if self._update_durable_object(obj):
                        logger.info(f"Updated Durable Object: {obj_name} (v{obj_version})")
                        successful_deployments += 1
                    else:
                        logger.error(f"Failed to update Durable Object: {obj_name}")
                else:
                    # Create new object
                    if self._create_durable_object(obj):
                        logger.info(f"Created Durable Object: {obj_name} (v{obj_version})")
                        successful_deployments += 1
                    else:
                        logger.error(f"Failed to create Durable Object: {obj_name}")
                
            except Exception as e:
                logger.error(f"Error deploying Durable Object {obj_name}: {str(e)}")
        
        success_rate = successful_deployments / total_objects if total_objects > 0 else 0
        logger.info(f"Deployment completed: {successful_deployments}/{total_objects} objects deployed successfully ({success_rate:.1%})")
        
        return successful_deployments == total_objects
    
    def _object_exists(self, name: str) -> bool:
        """
        Check if a Durable Object with the given name exists.
        
        Args:
            name: Name of the Durable Object to check
            
        Returns:
            True if the object exists, False otherwise
        """
        # This is a simplified implementation for demonstration
        # In a real implementation, this would make an API call to the registry service
        logger.info(f"Checking if Durable Object exists: {name}")
        return False
    
    def _create_durable_object(self, obj_config: Dict[str, Any]) -> bool:
        """
        Create a new Durable Object.
        
        Args:
            obj_config: Configuration for the Durable Object
            
        Returns:
            True if the object was created successfully, False otherwise
        """
        # This is a simplified implementation for demonstration
        # In a real implementation, this would make an API call to the registry service
        name = obj_config["name"]
        version = obj_config["version"]
        code_path = obj_config["code_path"]
        
        logger.info(f"Creating Durable Object: {name} (v{version})")
        
        # Simulate API call to create object
        time.sleep(0.5)
        
        # Simulate success
        return True
    
    def _update_durable_object(self, obj_config: Dict[str, Any]) -> bool:
        """
        Update an existing Durable Object.
        
        Args:
            obj_config: Configuration for the Durable Object
            
        Returns:
            True if the object was updated successfully, False otherwise
        """
        # This is a simplified implementation for demonstration
        # In a real implementation, this would make an API call to the registry service
        name = obj_config["name"]
        version = obj_config["version"]
        code_path = obj_config["code_path"]
        
        logger.info(f"Updating Durable Object: {name} to v{version}")
        
        # Simulate API call to update object
        time.sleep(0.5)
        
        # Simulate success
        return True
    
    def list_deployed_objects(self) -> List[Dict[str, Any]]:
        """
        List all currently deployed Durable Objects.
        
        Returns:
            List of deployed Durable Objects with their details
        """
        # This is a simplified implementation for demonstration
        # In a real implementation, this would make an API call to the registry service
        logger.info("Listing deployed Durable Objects")
        
        # Simulate API call to list objects
        time.sleep(0.5)
        
        # Simulate response with sample objects
        return [
            {"name": "AuthenticationDO", "version": "1.0.0", "status": "ACTIVE"},
            {"name": "UserManagementDO", "version": "1.2.1", "status": "ACTIVE"},
            {"name": "DataStorageDO", "version": "0.9.5", "status": "ACTIVE"},
        ]
    
    def delete_durable_object(self, name: str) -> bool:
        """
        Delete a Durable Object.
        
        Args:
            name: Name of the Durable Object to delete
            
        Returns:
            True if the object was deleted successfully, False otherwise
        """
        # This is a simplified implementation for demonstration
        # In a real implementation, this would make an API call to the registry service
        logger.info(f"Deleting Durable Object: {name}")
        
        # Simulate API call to delete object
        time.sleep(0.5)
        
        # Simulate success
        return True


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="AIDevOS Durable Objects Deployer")
    
    parser.add_argument(
        "--registry-url",
        type=str,
        default="http://localhost:8000/registry",
        help="URL of the Durable Objects registry service",
    )
    
    parser.add_argument(
        "--auth-token",
        type=str,
        help="Authentication token for the registry service",
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config/durable_objects.json",
        help="Path to the Durable Objects configuration file",
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all currently deployed Durable Objects",
    )
    
    parser.add_argument(
        "--delete",
        type=str,
        help="Delete a specific Durable Object by name",
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the Durable Objects deployer.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    deployer = DurableObjectDeployer(
        registry_url=args.registry_url,
        auth_token=args.auth_token,
        config_path=args.config,
    )
    
    if args.list:
        objects = deployer.list_deployed_objects()
        print("\nDeployed Durable Objects:")
        print("--------------------------")
        for obj in objects:
            print(f"{obj['name']} (v{obj['version']}): {obj['status']}")
        return 0
    
    if args.delete:
        if deployer.delete_durable_object(args.delete):
            print(f"\nSuccessfully deleted Durable Object: {args.delete}")
            return 0
        else:
            print(f"\nFailed to delete Durable Object: {args.delete}")
            return 1
    
    try:
        config = deployer.load_configuration()
    except (FileNotFoundError, json.JSONDecodeError):
        return 1
    
    if not deployer.validate_configuration(config):
        return 1
    
    if deployer.deploy_durable_objects(config):
        print("\nDurable Objects deployment completed successfully")
        return 0
    else:
        print("\nDurable Objects deployment completed with errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())