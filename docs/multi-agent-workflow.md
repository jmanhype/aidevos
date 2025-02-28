# AIDevOS Multi-Branch Development Workflow

## Overview

AIDevOS uses a multi-branch collaborative approach to automate the development, deployment, and evolution of SaaS applications. This document outlines how the different git branches work together and how the tmux-based workflow facilitates this collaboration.

## Branch Structure and Responsibilities

### 1. PM-Architecture Branch (`pm-architecture`)

**Focus**: System design, feature planning, and architecture
**Responsibilities**:
- Refine user requirements into structured software specifications
- Design system architecture and component interactions
- Create feature roadmaps and prioritize development tasks
- Ensure alignment between business requirements and technical implementation

### 2. Backend-DB Branch (`backend-db`)

**Focus**: API design, database models, and business logic
**Responsibilities**:
- Design and implement API endpoints and services
- Create database schemas and data models
- Implement business logic and core functionality
- Ensure scalability and performance of backend systems
- Implement Durable Objects as microservices

### 3. Frontend-UI Branch (`frontend-ui`)

**Focus**: UI/UX design, frontend components, and user interactions
**Responsibilities**:
- Design user interfaces and user experiences
- Implement frontend components and interactions
- Ensure responsive and accessible design
- Create intuitive user workflows and interactions

### 4. DevOps-QA Branch (`devops-qa`)

**Focus**: CI/CD pipeline, testing, deployment, and monitoring
**Responsibilities**:
- Design and implement CI/CD pipelines
- Create comprehensive test suites and testing strategies
- Set up monitoring and alerting systems
- Ensure security best practices are followed
- Optimize deployment processes and resource utilization

### 5. Main Branch (`main`)

**Focus**: Integration, merging, and release management
**Responsibilities**:
- Merge changes from feature branches
- Resolve conflicts and ensure compatibility
- Maintain a stable, production-ready codebase
- Coordinate releases and versioning
- Serve as the source of truth for the project

## Development Workflow

1. **Feature Planning**
   - New features are initially planned in the `pm-architecture` branch
   - Architecture diagrams and specifications are created
   - Tasks are defined and assigned to appropriate branches

2. **Parallel Development**
   - Each branch works on its assigned components independently
   - Regular commits document progress and changes
   - Each branch focuses on its specific domain expertise

3. **Integration and Testing**
   - Changes are periodically merged into the `main` branch
   - Conflicts are resolved during the merge process
   - Integrated system is tested to ensure compatibility

4. **Deployment and Feedback**
   - Stable versions from `main` are deployed
   - Feedback is collected and used to inform future development
   - Issues are addressed in the appropriate feature branches

## Using the tmux-based Workflow

The `setup-aidevos-team.sh` script creates a tmux session with 5 windows:
- 4 windows for the feature branches (PM-Architecture, Backend-DB, Frontend-UI, DevOps-QA)
- 1 window for the main branch (Merger)

### Basic tmux Commands

- `Ctrl-b d`: Detach from the tmux session (session keeps running in background)
- `tmux attach-session -t aidevos`: Reattach to the session
- `Ctrl-b n / Ctrl-b p`: Next/previous window
- `Ctrl-b c`: Create a new window
- `Ctrl-b ,`: Rename the current window
- `Ctrl-b ?`: Show help with all keybindings

### Git Commands for Branch Management

- `git status`: Check the current status of your branch
- `git log --all --decorate --oneline --graph`: Visualize branch history
- `git diff main..branch-name`: See differences between branches
- `git merge branch-name`: Merge changes from a branch into the current branch
- `git checkout -b new-branch`: Create and switch to a new branch

### Workflow Tips

1. Keep each window focused on its specific domain
2. Use the Merger window to monitor changes across all branches
3. Regularly pull changes from `main` into feature branches to stay up-to-date
4. Use meaningful commit messages to document changes
5. Resolve conflicts promptly to maintain a smooth workflow
