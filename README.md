# Autonomous Development System

An intelligent system for creating, modifying, and deploying code at runtime through natural language interactions.

## Overview

The Autonomous Development System is a self-modifying codebase that allows you to create and modify code through various interfaces including a web UI, voice commands, SMS, and more. The system uses AI to transform natural language descriptions into working code that can be deployed immediately.

## Key Features

### Object Management
- Create objects manually or using AI with `create_object_from_scratch/3`
- Modify existing objects with natural language prompts
- Deploy objects to different environments with `activate_object/1`
- Query objects by name with `get_object_by_name/1`
- Count total objects with `count_objects/0`
- List all objects with `list_objects/0`

### User Management
- List all users with `list_users/0`
- Count users with `count_users/0`
- User authentication with phone number registration

### Communication Channels
- **Voice Integration**: Make and receive calls via Twilio
- **SMS Integration**: Send and receive SMS messages via Twilio
- **Email Integration**: Send emails with Bamboo
- **Slack Integration**: Send messages to Slack channels
- **GitHub Integration**: Create issues and manage repositories

### AI-Powered Features
- **Agentic Reward Modeling**: Evaluate code modifications against human preferences
- **Constraint Checking**: Ensure code adheres to defined constraints
- **Factuality Verification**: Validate correctness of implemented algorithms
- **Code Generation**: Create new code from natural language descriptions
- **Voice Command Processing**: Parse and execute voice commands

### Event Monitoring
- Set up monitors for system events (e.g., "call me when a user signs up")
- Receive notifications via voice calls, SMS, email, or Slack

## Documentation

For detailed information about the system's features, please refer to:

- [Object Lifecycle Documentation](README.object_lifecycle.md) - How objects are created, activated, and managed
- [Voice Integration Documentation](README.voice_integration.md) - How to use voice commands with the system
- [SMS Integration Documentation](README.sms_integration.md) - How to use SMS commands with the system
- [Self-Modifying Objects Documentation](README_SELF_MODIFYING.md) - Details on the self-modifying code architecture
- [Command Parser Architecture](README.command_parser.md) - How natural language commands are parsed
- [Command Processor Architecture](README.command_processor.md) - How commands are executed

## Installation

1. Clone the repo
   ```
   git clone https://github.com/yourusername/self_modifying_objects.git
   ```
2. Install dependencies
   ```
   cd self_modifying_objects
   mix deps.get
   ```
3. Create a postgres database and run migration with ash_postgres
   ```
   mix ash.setup && mix ash.migrate
   ```
4. Set up environment variables
   ```
   cp env.example .env
   ```
   Edit the `.env` file to include your configuration for:
   - Twilio credentials for voice and SMS integration
   - Email service configuration
   - Slack API tokens
   - GitHub integration settings
   - OpenAI API key for AI features

### Test
1. Create a test database and run migration with ash_postgres
   ```
   MIX_ENV=test mix ash_postgres.create && MIX_ENV=test mix ash.migrate
   ```

2. Run the tests
   ```
   mix test
   ```

## Getting started

To start your Phoenix server:

  * Start Phoenix endpoint with `mix phx.server` or inside IEx with `iex -S mix phx.server`

Now you can visit [`localhost:4000`](http://localhost:4000) from your browser.

## Sending a Pull Request
The consultants at Alembic are monitoring for pull requests when they are "on the beach" (aka when they are not billable or working with a client). We will review your pull request and either merge it, request changes to it, or close it with an explanation. For changes raised when there are no consultants on the beach, please expect some delay. We will do our best to provide update and feedback throughout the process.

---

## About the Original Template

This project was initially based on the RealWorld template, a demonstration of a fully fledged fullstack application built with Ash + Phoenix LiveView.

> ### Ash + Phoenix LiveView codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.

For more information on the original template, visit the [RealWorld](https://github.com/gothinkster/realworld) repo.

> ### [Demo](https://realworld-ash.fly.dev/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)

This codebase was created to demonstrate a fully fledged fullstack application built with **Ash** + **Phoenix LiveView** including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the **Ash** + **Phoenix LiveView** community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.
