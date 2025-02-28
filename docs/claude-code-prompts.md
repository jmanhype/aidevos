# Claude Code Prompts for AIDevOS Multi-Agent Workflow

This document provides specialized prompts for each agent role in the AIDevOS multi-agent workflow. These prompts are designed to be used with Claude Code in each tmux window to maximize the effectiveness of the AI-driven development process.

## PM & Architecture Agent Prompts

```bash
# Initial project assessment
claude "Analyze the current state of the AIDevOS project. Identify the key components, their relationships, and any architectural gaps or inconsistencies."

# Architecture refinement
claude "Based on the current architecture, suggest improvements to enhance scalability, maintainability, and performance. Focus on the interaction between Durable Objects and the orchestration layer."

# Feature planning
claude "Create a prioritized feature roadmap for the next development cycle. Consider user needs, technical debt, and implementation complexity."

# Task breakdown
claude "Break down the implementation of [specific feature] into discrete tasks that can be assigned to the Backend, Frontend, and DevOps agents."

# Architecture documentation
claude "Generate comprehensive documentation for the current system architecture, including component diagrams, data flow diagrams, and sequence diagrams using Mermaid syntax."
```

## Backend & Database Agent Prompts

```bash
# API design
claude "Design a RESTful API for the [specific feature] with OpenAPI specification. Include endpoint definitions, request/response schemas, and error handling."

# Database schema
claude "Create a database schema for [specific feature]. Include entity relationships, indexes, and consider performance optimization for common queries."

# Durable Object implementation
claude "Implement a Durable Object for [specific service]. Focus on state management, lifecycle hooks, and communication with other objects."

# Business logic
claude "Implement the business logic for [specific feature]. Ensure proper validation, error handling, and integration with the existing codebase."

# Performance optimization
claude "Analyze the current implementation of [specific component] and suggest optimizations to improve performance, reduce latency, and enhance scalability."
```

## Frontend & UI Agent Prompts

```bash
# UI component design
claude "Design a UI component for [specific feature]. Include HTML, CSS, and JavaScript code with a focus on responsiveness, accessibility, and user experience."

# State management
claude "Implement state management for [specific feature]. Consider user interactions, API integration, and error handling."

# UI testing
claude "Create comprehensive tests for the [specific UI component]. Include unit tests, integration tests, and end-to-end tests."

# Responsive design
claude "Optimize the [specific UI component] for mobile devices. Ensure proper rendering on different screen sizes and touch interaction support."

# Accessibility improvements
claude "Audit the [specific UI component] for accessibility issues and implement fixes to ensure compliance with WCAG 2.1 AA standards."
```

## DevOps & QA Agent Prompts

```bash
# CI/CD pipeline
claude "Design a CI/CD pipeline for the AIDevOS project. Include stages for building, testing, and deploying the application."

# Test automation
claude "Create an automated testing strategy for the AIDevOS project. Include unit tests, integration tests, and end-to-end tests."

# Deployment configuration
claude "Configure the deployment process for Durable Objects. Ensure proper versioning, rollback capabilities, and monitoring."

# Infrastructure as code
claude "Create infrastructure as code for the AIDevOS project. Use Terraform or similar tools to define the required resources."

# Monitoring and alerting
claude "Design a monitoring and alerting system for the AIDevOS project. Include metrics collection, log aggregation, and alert configuration."
```

## Security Agent Prompts

```bash
# Security audit
claude "Perform a security audit of the [specific component]. Identify potential vulnerabilities and suggest mitigations."

# Authentication and authorization
claude "Implement authentication and authorization for the AIDevOS API. Consider JWT, OAuth, or other appropriate protocols."

# Data protection
claude "Review the data handling in [specific component] and suggest improvements to ensure data protection and privacy compliance."

# Secure coding practices
claude "Analyze the code in [specific file] for security vulnerabilities. Suggest improvements based on secure coding practices."

# Security testing
claude "Create security tests for the AIDevOS project. Include tests for common vulnerabilities like SQL injection, XSS, and CSRF."
```

## Merger & Integration Agent Prompts

```bash
# Code review
claude "Review the changes in the [specific branch] and provide feedback on code quality, potential issues, and adherence to best practices."

# Conflict resolution
claude "Analyze the merge conflicts between [branch1] and [branch2]. Suggest resolutions that preserve the functionality of both branches."

# Integration testing
claude "Create integration tests to verify that the changes in [specific branch] work correctly with the existing codebase."

# Release preparation
claude "Prepare a release plan for version [X.Y.Z]. Include a changelog, deployment steps, and rollback procedures."

# Documentation update
claude "Update the project documentation to reflect the changes in version [X.Y.Z]. Focus on API changes, new features, and breaking changes."
```

## Using These Prompts in the tmux Setup

You can incorporate these prompts into your `setup-aidevos-team.sh` script to automatically initialize each Claude Code instance with the appropriate context. For example:

```bash
# Configure the PM-Architecture window
tmux send-keys "cd ~/aidevos && git checkout pm-architecture" C-m
tmux send-keys "echo 'Claude Instance 1 - PM & Architecture Agent'" C-m
tmux send-keys "claude \"Analyze the current state of the AIDevOS project. Identify the key components, their relationships, and any architectural gaps or inconsistencies.\"" C-m

# Configure the Backend-DB window
tmux send-keys "cd ~/aidevos && git checkout backend-db" C-m
tmux send-keys "echo 'Claude Instance 2 - Backend & Database Agent'" C-m
tmux send-keys "claude \"Design a RESTful API for the core features with OpenAPI specification. Include endpoint definitions, request/response schemas, and error handling.\"" C-m
```

## Best Practices for Prompt Engineering

1. **Be specific**: Clearly define the task, context, and expected output
2. **Provide context**: Include relevant information about the current state of the project
3. **Set constraints**: Specify any limitations or requirements that should be considered
4. **Request format**: Indicate the desired format for the response (code, documentation, etc.)
5. **Break down complex tasks**: Split large tasks into smaller, more manageable prompts
6. **Iterate**: Refine prompts based on the responses to get better results

By using these specialized prompts, each agent in the AIDevOS multi-agent workflow can leverage Claude Code more effectively, resulting in higher quality code, better architecture, and a more efficient development process.
