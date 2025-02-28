#!/bin/bash

# Kill any existing tmux sessions
tmux kill-session -t aidevos 2>/dev/null

# Create a new tmux session
tmux new-session -d -s aidevos

# Split the window into 4 panes for the Claude instances
tmux split-window -h -t aidevos
tmux split-window -v -t aidevos:0.0
tmux split-window -v -t aidevos:0.1

# Name the panes
tmux select-pane -t aidevos:0.0
tmux send-keys "echo 'Claude Instance 1 - PM & Architecture'" C-m
tmux select-pane -t aidevos:0.1
tmux send-keys "echo 'Claude Instance 2 - Backend'" C-m
tmux select-pane -t aidevos:0.2
tmux send-keys "echo 'Claude Instance 3 - Frontend'" C-m
tmux select-pane -t aidevos:0.3
tmux send-keys "echo 'Claude Instance 4 - DevOps & QA'" C-m

# Create a new window for the merger
tmux new-window -t aidevos:1 -n "Merger"
tmux send-keys "echo 'Merger - Combines outputs from all Claude instances'" C-m

# Return to the first window
tmux select-window -t aidevos:0

# Attach to the session
tmux attach-session -t aidevos

echo "AIDevOS tmux session started with 4 Claude instances and 1 merger."
