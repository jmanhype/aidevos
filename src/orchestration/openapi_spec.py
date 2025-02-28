"""
AIDevOS OpenAPI Specification Generator

This module generates an OpenAPI specification for the AIDevOS API,
documenting all available endpoints, request/response formats, and authentication.
"""

import json
from typing import Dict, Any

# OpenAPI specification version
OPENAPI_VERSION = "3.0.0"


def generate_openapi_spec() -> Dict[str, Any]:
    """
    Generate the OpenAPI specification for AIDevOS
    
    Returns:
        OpenAPI specification as a dictionary
    """
    spec = {
        "openapi": OPENAPI_VERSION,
        "info": {
            "title": "AIDevOS API",
            "description": "API for the AIDevOS system, providing access to Durable Objects, users, and data.",
            "version": "1.0.0",
            "contact": {
                "name": "AIDevOS Team",
                "url": "https://aidevos.io",
                "email": "support@aidevos.io"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "https://api.aidevos.io/v1",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.aidevos.io/v1",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000/v1",
                "description": "Local development server"
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT token obtained from the /auth/login endpoint"
                },
                "apiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API key obtained from the system administrator"
                }
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "description": "Error message"
                        },
                        "status_code": {
                            "type": "integer",
                            "description": "HTTP status code"
                        }
                    },
                    "required": ["error"]
                },
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "User ID"
                        },
                        "username": {
                            "type": "string",
                            "description": "Username"
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Email address"
                        },
                        "roles": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "User roles"
                        },
                        "first_name": {
                            "type": "string",
                            "description": "First name"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Last name"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Creation timestamp"
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Whether the user is active"
                        }
                    },
                    "required": ["id", "username", "email", "roles"]
                },
                "Project": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Project ID"
                        },
                        "name": {
                            "type": "string",
                            "description": "Project name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description"
                        },
                        "owner_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Owner user ID"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Creation timestamp"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "archived", "deleted"],
                            "description": "Project status"
                        }
                    },
                    "required": ["id", "name", "owner_id", "status"]
                },
                "DurableObject": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Object ID"
                        },
                        "name": {
                            "type": "string",
                            "description": "Object name"
                        },
                        "type": {
                            "type": "string",
                            "description": "Object type"
                        },
                        "project_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Project ID"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["initializing", "active", "idle", "hibernating", "terminating"],
                            "description": "Object status"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Creation timestamp"
                        },
                        "updated_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Last update timestamp"
                        },
                        "last_activity": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Last activity timestamp"
                        }
                    },
                    "required": ["id", "name", "type", "project_id", "status"]
                },
                "LoginRequest": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Username"
                        },
                        "password": {
                            "type": "string",
                            "format": "password",
                            "description": "Password"
                        }
                    },
                    "required": ["username", "password"]
                },
                "LoginResponse": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean",
                            "description": "Whether the login was successful"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "JWT access token"
                        },
                        "refresh_token": {
                            "type": "string",
                            "description": "JWT refresh token"
                        },
                        "user": {
                            "$ref": "#/components/schemas/User"
                        }
                    },
                    "required": ["success", "access_token", "refresh_token", "user"]
                }
            }
        },
        "paths": {
            # Authentication endpoints
            "/auth/login": {
                "post": {
                    "summary": "Login to the system",
                    "description": "Authenticate with username and password to get access tokens",
                    "tags": ["Authentication"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LoginRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful login",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LoginResponse"
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Invalid credentials",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/auth/register": {
                "post": {
                    "summary": "Register a new user",
                    "description": "Create a new user account",
                    "tags": ["Authentication"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {
                                            "type": "string",
                                            "description": "Username"
                                        },
                                        "email": {
                                            "type": "string",
                                            "format": "email",
                                            "description": "Email address"
                                        },
                                        "password": {
                                            "type": "string",
                                            "format": "password",
                                            "description": "Password"
                                        },
                                        "first_name": {
                                            "type": "string",
                                            "description": "First name"
                                        },
                                        "last_name": {
                                            "type": "string",
                                            "description": "Last name"
                                        }
                                    },
                                    "required": ["username", "email", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful registration",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the registration was successful"
                                            },
                                            "message": {
                                                "type": "string",
                                                "description": "Success message"
                                            },
                                            "user_id": {
                                                "type": "string",
                                                "format": "uuid",
                                                "description": "ID of the created user"
                                            }
                                        },
                                        "required": ["success", "message", "user_id"]
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid registration data",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/auth/refresh": {
                "post": {
                    "summary": "Refresh access token",
                    "description": "Get a new access token using a refresh token",
                    "tags": ["Authentication"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "refresh_token": {
                                            "type": "string",
                                            "description": "Refresh token"
                                        }
                                    },
                                    "required": ["refresh_token"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful token refresh",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the refresh was successful"
                                            },
                                            "access_token": {
                                                "type": "string",
                                                "description": "New JWT access token"
                                            }
                                        },
                                        "required": ["success", "access_token"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Invalid refresh token",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/auth/logout": {
                "post": {
                    "summary": "Logout from the system",
                    "description": "Invalidate the current access token",
                    "tags": ["Authentication"],
                    "security": [
                        {"bearerAuth": []}
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful logout",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the logout was successful"
                                            },
                                            "message": {
                                                "type": "string",
                                                "description": "Success message"
                                            }
                                        },
                                        "required": ["success", "message"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # User endpoints
            "/users": {
                "get": {
                    "summary": "List users",
                    "description": "Get a list of users in the system (admin only)",
                    "tags": ["Users"],
                    "security": [
                        {"bearerAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "role",
                            "in": "query",
                            "description": "Filter by role",
                            "schema": {
                                "type": "string"
                            }
                        },
                        {
                            "name": "active_only",
                            "in": "query",
                            "description": "Only include active users",
                            "schema": {
                                "type": "boolean",
                                "default": True
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of users",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the request was successful"
                                            },
                                            "users": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/User"
                                                },
                                                "description": "List of users"
                                            },
                                            "total": {
                                                "type": "integer",
                                                "description": "Total number of users"
                                            }
                                        },
                                        "required": ["success", "users", "total"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/users/{user_id}": {
                "get": {
                    "summary": "Get user",
                    "description": "Get a user by ID",
                    "tags": ["Users"],
                    "security": [
                        {"bearerAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "description": "User ID",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "format": "uuid"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User details",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the request was successful"
                                            },
                                            "user": {
                                                "$ref": "#/components/schemas/User"
                                            }
                                        },
                                        "required": ["success", "user"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "User not found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                },
                "put": {
                    "summary": "Update user",
                    "description": "Update a user's profile",
                    "tags": ["Users"],
                    "security": [
                        {"bearerAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "description": "User ID",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "format": "uuid"
                            }
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "updates": {
                                            "type": "object",
                                            "properties": {
                                                "first_name": {
                                                    "type": "string",
                                                    "description": "First name"
                                                },
                                                "last_name": {
                                                    "type": "string",
                                                    "description": "Last name"
                                                },
                                                "email": {
                                                    "type": "string",
                                                    "format": "email",
                                                    "description": "Email address"
                                                },
                                                "password": {
                                                    "type": "string",
                                                    "format": "password",
                                                    "description": "New password"
                                                },
                                                "settings": {
                                                    "type": "object",
                                                    "description": "User settings"
                                                }
                                            }
                                        }
                                    },
                                    "required": ["updates"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "User updated",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the update was successful"
                                            },
                                            "message": {
                                                "type": "string",
                                                "description": "Success message"
                                            }
                                        },
                                        "required": ["success", "message"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "User not found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # Durable Objects endpoints
            "/durable-objects": {
                "get": {
                    "summary": "List Durable Objects",
                    "description": "Get a list of Durable Objects in the system (admin only)",
                    "tags": ["Durable Objects"],
                    "security": [
                        {"bearerAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "project_id",
                            "in": "query",
                            "description": "Filter by project ID",
                            "schema": {
                                "type": "string",
                                "format": "uuid"
                            }
                        },
                        {
                            "name": "object_type",
                            "in": "query",
                            "description": "Filter by object type",
                            "schema": {
                                "type": "string"
                            }
                        },
                        {
                            "name": "status",
                            "in": "query",
                            "description": "Filter by status",
                            "schema": {
                                "type": "string",
                                "enum": ["initializing", "active", "idle", "hibernating", "terminating"]
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of Durable Objects",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the request was successful"
                                            },
                                            "objects": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/DurableObject"
                                                },
                                                "description": "List of Durable Objects"
                                            },
                                            "total": {
                                                "type": "integer",
                                                "description": "Total number of objects"
                                            }
                                        },
                                        "required": ["success", "objects", "total"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Create Durable Object",
                    "description": "Create a new Durable Object (admin only)",
                    "tags": ["Durable Objects"],
                    "security": [
                        {"bearerAuth": []}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "type_name": {
                                            "type": "string",
                                            "description": "Type of Durable Object to create"
                                        },
                                        "project_id": {
                                            "type": "string",
                                            "format": "uuid",
                                            "description": "Project ID"
                                        },
                                        "name": {
                                            "type": "string",
                                            "description": "Object name"
                                        },
                                        "initial_state": {
                                            "type": "object",
                                            "description": "Initial state for the object"
                                        }
                                    },
                                    "required": ["type_name", "project_id", "name"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Object created",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the creation was successful"
                                            },
                                            "object_id": {
                                                "type": "string",
                                                "format": "uuid",
                                                "description": "ID of the created object"
                                            },
                                            "message": {
                                                "type": "string",
                                                "description": "Success message"
                                            }
                                        },
                                        "required": ["success", "object_id", "message"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # Data storage endpoints
            "/data/collections": {
                "get": {
                    "summary": "List collections",
                    "description": "Get a list of data collections",
                    "tags": ["Data Storage"],
                    "security": [
                        {"bearerAuth": []},
                        {"apiKeyAuth": []}
                    ],
                    "responses": {
                        "200": {
                            "description": "List of collections",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "description": "Whether the request was successful"
                                            },
                                            "collections": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {
                                                            "type": "string",
                                                            "description": "Collection name"
                                                        },
                                                        "item_count": {
                                                            "type": "integer",
                                                            "description": "Number of items in the collection"
                                                        }
                                                    },
                                                    "required": ["name", "item_count"]
                                                },
                                                "description": "List of collections"
                                            },
                                            "total": {
                                                "type": "integer",
                                                "description": "Total number of collections"
                                            }
                                        },
                                        "required": ["success", "collections", "total"]
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    return spec


def save_openapi_spec(output_path: str) -> None:
    """
    Generate and save the OpenAPI specification to a file
    
    Args:
        output_path: Path to save the specification to
    """
    spec = generate_openapi_spec()
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)
    print(f"OpenAPI specification saved to {output_path}")


if __name__ == "__main__":
    save_openapi_spec("openapi.json")
"""