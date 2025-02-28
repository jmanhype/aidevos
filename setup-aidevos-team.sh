#!/bin/bash

# Kill any existing tmux sessions
tmux kill-session -t aidevos 2>/dev/null

# Create project structure if it doesn't exist
mkdir -p ~/aidevos/src/{agents,orchestration,deployment,monitoring,utils}
mkdir -p ~/aidevos/tests
mkdir -p ~/aidevos/docs

# Initialize git repository if it doesn't exist
cd ~/aidevos
if [ ! -d .git ]; then
  git init
  echo "# AIDevOS - AI-Driven Autonomous DevOps System" > README.md
  git add README.md
  git commit -m "Initial commit"
fi

# Create branches if they don't exist
git checkout -b main 2>/dev/null || git checkout main
git branch pm-architecture 2>/dev/null || echo "Branch pm-architecture already exists"
git branch backend-db 2>/dev/null || echo "Branch backend-db already exists"
git branch frontend-ui 2>/dev/null || echo "Branch frontend-ui already exists"
git branch devops-qa 2>/dev/null || echo "Branch devops-qa already exists"

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo "Claude command not found. Please make sure Claude is installed and in your PATH."
    echo "Continuing setup without launching Claude automatically."
    CLAUDE_EXISTS=false
else
    CLAUDE_EXISTS=true
fi

# Create a new tmux session
tmux new-session -d -s aidevos -n "PM-Architecture"

# Configure the first window for PM & Architecture
tmux send-keys "cd ~/aidevos && git checkout pm-architecture" C-m
tmux send-keys "echo 'Claude Instance 1 - PM & Architecture Agent'" C-m
tmux send-keys "echo 'Focus: System design, feature planning, and architecture'" C-m
if [ "$CLAUDE_EXISTS" = true ]; then
    tmux send-keys "claude" C-m
fi

# Create and configure window for Backend & Database
tmux new-window -t aidevos:1 -n "Backend-DB"
tmux send-keys "cd ~/aidevos && git checkout backend-db" C-m
tmux send-keys "echo 'Claude Instance 2 - Backend & Database Agent'" C-m
tmux send-keys "echo 'Focus: API design, database models, and business logic'" C-m
if [ "$CLAUDE_EXISTS" = true ]; then
    tmux send-keys "claude" C-m
fi

# Create and configure window for Frontend & UI
tmux new-window -t aidevos:2 -n "Frontend-UI"
tmux send-keys "cd ~/aidevos && git checkout frontend-ui" C-m
tmux send-keys "echo 'Claude Instance 3 - Frontend & UI Agent'" C-m
tmux send-keys "echo 'Focus: UI/UX design, frontend components, and user interactions'" C-m
if [ "$CLAUDE_EXISTS" = true ]; then
    tmux send-keys "claude" C-m
fi

# Create and configure window for DevOps & QA
tmux new-window -t aidevos:3 -n "DevOps-QA"
tmux send-keys "cd ~/aidevos && git checkout devops-qa" C-m
tmux send-keys "echo 'Claude Instance 4 - DevOps & QA Agent'" C-m
tmux send-keys "echo 'Focus: CI/CD pipeline, testing, deployment, and monitoring'" C-m
if [ "$CLAUDE_EXISTS" = true ]; then
    tmux send-keys "claude" C-m
fi

# Create and configure window for the Merger/Monitor
tmux new-window -t aidevos:4 -n "Merger"
tmux send-keys "cd ~/aidevos && git checkout main" C-m
tmux send-keys "echo 'Merger - Monitors and merges changes from all branches'" C-m
tmux send-keys "echo 'Commands to monitor branches:'" C-m
tmux send-keys "echo '  git log --all --decorate --oneline --graph'" C-m
tmux send-keys "echo '  git branch -a'" C-m
tmux send-keys "echo '  git diff main..pm-architecture'" C-m
if [ "$CLAUDE_EXISTS" = true ]; then
    tmux send-keys "claude" C-m
fi

# Return to the first window
tmux select-window -t aidevos:0

# Attach to the session
tmux attach-session -t aidevos

echo "AIDevOS tmux session started with 4 branch windows and 1 merger window."
if [ "$CLAUDE_EXISTS" = true ]; then
    echo "Claude has been launched in each window."
else
    echo "Claude was not found. Please launch Claude manually in each window."
fi
