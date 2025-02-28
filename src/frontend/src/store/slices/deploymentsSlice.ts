import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface DurableObject {
  id: string;
  name: string;
  status: 'created' | 'running' | 'stopped' | 'error';
  type: string;
  version: string;
  createdAt: string;
  lastUpdated: string;
  metadata: Record<string, any>;
  dependencies: string[];
}

export interface Deployment {
  id: string;
  name: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  startTime: string;
  endTime?: string;
  durableObjects: DurableObject[];
  logs: DeploymentLog[];
  createdBy: string;
}

export interface DeploymentLog {
  id: string;
  deploymentId: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  timestamp: string;
  source: string;
}

interface DeploymentsState {
  deployments: Deployment[];
  selectedDeploymentId: string | null;
  durableObjects: DurableObject[];
  isLoading: boolean;
  error: string | null;
}

const initialState: DeploymentsState = {
  deployments: [],
  selectedDeploymentId: null,
  durableObjects: [],
  isLoading: false,
  error: null,
};

export const deploymentsSlice = createSlice({
  name: 'deployments',
  initialState,
  reducers: {
    setDeployments: (state, action: PayloadAction<Deployment[]>) => {
      state.deployments = action.payload;
    },
    addDeployment: (state, action: PayloadAction<Deployment>) => {
      state.deployments.push(action.payload);
    },
    updateDeployment: (state, action: PayloadAction<{ id: string; updates: Partial<Deployment> }>) => {
      const index = state.deployments.findIndex(deployment => deployment.id === action.payload.id);
      if (index !== -1) {
        state.deployments[index] = { 
          ...state.deployments[index], 
          ...action.payload.updates 
        };
      }
    },
    selectDeployment: (state, action: PayloadAction<string | null>) => {
      state.selectedDeploymentId = action.payload;
    },
    setDurableObjects: (state, action: PayloadAction<DurableObject[]>) => {
      state.durableObjects = action.payload;
    },
    addDurableObject: (state, action: PayloadAction<DurableObject>) => {
      state.durableObjects.push(action.payload);
    },
    updateDurableObject: (state, action: PayloadAction<{ id: string; updates: Partial<DurableObject> }>) => {
      const index = state.durableObjects.findIndex(obj => obj.id === action.payload.id);
      if (index !== -1) {
        state.durableObjects[index] = { 
          ...state.durableObjects[index], 
          ...action.payload.updates 
        };
      }
    },
    addDeploymentLog: (state, action: PayloadAction<DeploymentLog>) => {
      const deploymentIndex = state.deployments.findIndex(
        deployment => deployment.id === action.payload.deploymentId
      );
      if (deploymentIndex !== -1) {
        state.deployments[deploymentIndex].logs.push(action.payload);
      }
    },
    setDeploymentsLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setDeploymentsError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setDeployments,
  addDeployment,
  updateDeployment,
  selectDeployment,
  setDurableObjects,
  addDurableObject,
  updateDurableObject,
  addDeploymentLog,
  setDeploymentsLoading,
  setDeploymentsError,
} = deploymentsSlice.actions;

export default deploymentsSlice.reducer;