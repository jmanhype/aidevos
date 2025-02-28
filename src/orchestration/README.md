# AIDevOS Backend Architecture

This document provides an overview of the AIDevOS backend architecture, focusing on the Durable Objects microservices pattern, database models, and API design.

## Core Components

### 1. Durable Objects Framework

Durable Objects are isolated, self-contained units of computation that maintain their own state and respond to requests. They form the backbone of the microservices architecture in AIDevOS.

Key components of the Durable Objects framework:

- **BaseDurableObject**: Abstract base class for all Durable Objects
- **DurableObjectRegistry**: Manages Durable Object types and instances
- **DurableObjectRouter**: Routes requests to appropriate Durable Objects
- **EventBus**: Facilitates communication between Durable Objects

### 2. Database Models

The database layer provides a clean interface for storing and retrieving data while abstracting the underlying database implementation.

Key database models:

- **User**: Represents a system user with authentication and profile information
- **Project**: Represents a development project with metadata and member relationships
- **DurableObject**: Represents a Durable Object instance and its state
- **APIKey**: Represents an API key for external access
- **Task**: Represents a task or unit of work

### 3. Specialized Durable Objects

The system includes several specialized Durable Objects that provide core functionality:

- **AuthenticationDO**: Handles user authentication, authorization, and session management
- **UserManagementDO**: Manages user profiles, settings, and user-related operations
- **DataStorageDO**: Provides persistent data storage and retrieval capabilities
- **APIGatewayDO**: Manages API requests, routing, and API key management

### 4. API Service Layer

The API service layer exposes the functionality of Durable Objects through RESTful APIs:

- **APIRouter**: Base class for all API routers
- **AuthRouter**: Handles authentication endpoints
- **UserRouter**: Handles user management endpoints
- **DataRouter**: Handles data storage endpoints
- **ProjectRouter**: Handles project management endpoints
- **DurableObjectRouter**: Handles Durable Object management endpoints

## Architecture Diagrams

### Durable Objects Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  API Request │────▶│ API Service  │────▶│ API Router   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Durable      │◀───▶│ Durable Obj  │◀────│ Request      │
│ Object       │     │ Registry     │     │ Router       │
└──────────────┘     └──────────────┘     └──────────────┘
       │                                         ▲
       │                                         │
       ▼                                         │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Database     │◀───▶│ Data Store   │◀───▶│ Response     │
│ Layer        │     │ Interface    │     │ Handler      │
└──────────────┘     └──────────────┘     └──────────────┘
```

### API Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Client      │────▶│ Authentication│────▶│ Rate Limiting│
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Request      │◀───▶│ API Service  │◀───▶│ API Router   │
│ Validation   │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │                         │
┌─────────────▼─────┐         ┌────────▼───────────┐
│ Durable Object    │         │ Event Publication  │
│ Request Processing│         │                    │
└───────────────────┘         └────────────────────┘
              │                         │
              ▼                         ▼
┌──────────────────────┐      ┌────────────────────┐
│ Response Formatting  │      │ Async Processing   │
└──────────────────────┘      └────────────────────┘
```

## API Documentation

The API is documented using the OpenAPI Specification. Key endpoints include:

### Authentication Endpoints

- `POST /auth/login`: Authenticate with username and password
- `POST /auth/register`: Register a new user
- `POST /auth/refresh`: Refresh an access token
- `POST /auth/logout`: Logout and invalidate tokens

### User Management Endpoints

- `GET /users`: List all users (admin only)
- `GET /users/{user_id}`: Get a user by ID
- `PUT /users/{user_id}`: Update a user's profile
- `POST /users/{user_id}/deactivate`: Deactivate a user (admin only)
- `POST /users/{user_id}/activate`: Activate a user (admin only)

### Data Storage Endpoints

- `GET /data/collections`: List all data collections
- `GET /data/collections/{collection}`: Query a collection
- `POST /data/collections/{collection}`: Store data in a collection
- `GET /data/collections/{collection}/{item_id}`: Get an item by ID
- `PUT /data/collections/{collection}/{item_id}`: Update an item
- `DELETE /data/collections/{collection}/{item_id}`: Delete an item

### Durable Object Management Endpoints

- `GET /durable-objects`: List all Durable Objects (admin only)
- `POST /durable-objects`: Create a new Durable Object (admin only)
- `GET /durable-objects/{object_id}`: Get a Durable Object by ID (admin only)
- `PUT /durable-objects/{object_id}`: Update a Durable Object (admin only)
- `DELETE /durable-objects/{object_id}`: Delete a Durable Object (admin only)
- `POST /durable-objects/{object_id}/request`: Send a request to a Durable Object (admin only)

## Security Features

The system implements several security features:

1. **Authentication**: JWT-based authentication with access and refresh tokens
2. **Authorization**: Role-based access control for API endpoints
3. **API Keys**: Support for API keys with fine-grained permissions
4. **Rate Limiting**: Protection against abuse and DoS attacks
5. **CSRF Protection**: Prevention of cross-site request forgery attacks
6. **Input Sanitization**: Prevention of injection attacks

## Database Storage

The current implementation uses an in-memory database store for development and testing. In production, this would be replaced with a persistent database implementation, such as:

- PostgreSQL for relational data
- MongoDB for document data
- Redis for caching and temporary storage

## Performance Optimization

The system is designed for high performance:

1. **Asynchronous Processing**: All operations are asynchronous for maximum throughput
2. **State Management**: Durable Objects maintain their own state for quick access
3. **Hibernation**: Objects can hibernate when idle to conserve resources
4. **Event-Driven Communication**: Objects communicate via events for loose coupling
5. **Caching**: Frequently accessed data can be cached for rapid retrieval

## Development and Testing

To run the backend services:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API service
python -m src.orchestration.api_service

# Generate OpenAPI specification
python -m src.orchestration.openapi_spec
```

## Next Steps

1. Implement persistent database storage adapters
2. Add comprehensive test coverage
3. Implement additional specialized Durable Objects
4. Enhance security with multi-factor authentication
5. Add monitoring and logging infrastructure