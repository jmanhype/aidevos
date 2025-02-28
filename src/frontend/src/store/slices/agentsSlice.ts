import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Agent {
  id: string;
  name: string;
  type: 'PM' | 'Backend' | 'Frontend' | 'DevOps' | 'QA' | 'Security';
  status: 'idle' | 'active' | 'error';
  currentTask?: string;
  lastActive: string;
  capabilities: string[];
}

export interface AgentMessage {
  id: string;
  agentId: string;
  content: string;
  timestamp: string;
  replyTo?: string;
}

interface AgentsState {
  agents: Agent[];
  selectedAgentId: string | null;
  messages: AgentMessage[];
  isLoading: boolean;
  error: string | null;
}

const initialState: AgentsState = {
  agents: [],
  selectedAgentId: null,
  messages: [],
  isLoading: false,
  error: null,
};

export const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    setAgents: (state, action: PayloadAction<Agent[]>) => {
      state.agents = action.payload;
    },
    addAgent: (state, action: PayloadAction<Agent>) => {
      state.agents.push(action.payload);
    },
    updateAgent: (state, action: PayloadAction<{ id: string; updates: Partial<Agent> }>) => {
      const index = state.agents.findIndex(agent => agent.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = { ...state.agents[index], ...action.payload.updates };
      }
    },
    removeAgent: (state, action: PayloadAction<string>) => {
      state.agents = state.agents.filter(agent => agent.id !== action.payload);
    },
    selectAgent: (state, action: PayloadAction<string | null>) => {
      state.selectedAgentId = action.payload;
    },
    setAgentMessages: (state, action: PayloadAction<AgentMessage[]>) => {
      state.messages = action.payload;
    },
    addAgentMessage: (state, action: PayloadAction<AgentMessage>) => {
      state.messages.push(action.payload);
    },
    setAgentsLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setAgentsError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setAgents,
  addAgent,
  updateAgent,
  removeAgent,
  selectAgent,
  setAgentMessages,
  addAgentMessage,
  setAgentsLoading,
  setAgentsError,
} = agentsSlice.actions;

export default agentsSlice.reducer;