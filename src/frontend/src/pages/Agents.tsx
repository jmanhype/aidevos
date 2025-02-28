import React from 'react';
import { 
  UserGroupIcon, 
  PlusIcon, 
  ArrowPathIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';

// Mock data for demo
const agentsData = [
  { 
    id: '1', 
    name: 'PM Agent', 
    status: 'active', 
    type: 'PM', 
    lastActive: '2 minutes ago',
    capabilities: ['Architecture design', 'Task planning', 'Feature prioritization'],
    description: 'Responsible for managing project requirements and coordinating between other agents.'
  },
  { 
    id: '2', 
    name: 'Backend Agent', 
    status: 'active', 
    type: 'Backend', 
    lastActive: '5 minutes ago',
    capabilities: ['API design', 'Database modeling', 'Business logic implementation'],
    description: 'Develops server-side logic, database schemas, and ensures scalability of backend systems.'
  },
  { 
    id: '3', 
    name: 'Frontend Agent', 
    status: 'active', 
    type: 'Frontend', 
    lastActive: 'Just now',
    capabilities: ['UI component design', 'State management', 'API integration'],
    description: 'Creates intuitive user interfaces and responsive designs with a focus on usability.'
  },
  { 
    id: '4', 
    name: 'DevOps Agent', 
    status: 'idle', 
    type: 'DevOps', 
    lastActive: '15 minutes ago',
    capabilities: ['CI/CD pipeline', 'Infrastructure as code', 'Deployment automation'],
    description: 'Manages deployment infrastructure and ensures smooth operation of deployed services.'
  },
  { 
    id: '5', 
    name: 'QA Agent', 
    status: 'idle', 
    type: 'QA', 
    lastActive: '30 minutes ago',
    capabilities: ['Test automation', 'Quality assurance', 'Bug reporting'],
    description: 'Creates and runs tests to ensure code quality and identify potential issues.'
  },
  { 
    id: '6', 
    name: 'Security Agent', 
    status: 'error', 
    type: 'Security', 
    lastActive: '2 hours ago',
    capabilities: ['Vulnerability scanning', 'Security best practices', 'Code review'],
    description: 'Reviews code for security vulnerabilities and ensures secure coding practices.'
  },
];

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'active':
      return 'badge-green';
    case 'idle':
      return 'badge-yellow';
    case 'error':
      return 'badge-red';
    default:
      return 'badge-blue';
  }
};

const getTypeIconColor = (type: string) => {
  switch (type) {
    case 'PM':
      return 'text-blue-500';
    case 'Backend':
      return 'text-green-500';
    case 'Frontend':
      return 'text-purple-500';
    case 'DevOps':
      return 'text-orange-500';
    case 'QA':
      return 'text-yellow-500';
    case 'Security':
      return 'text-red-500';
    default:
      return 'text-gray-500';
  }
};

const Agents = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Agents</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage and monitor AI agents in the system
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-outline">
            <ArrowPathIcon className="h-5 w-5 mr-1" />
            Refresh
          </button>
          <button className="btn btn-primary">
            <PlusIcon className="h-5 w-5 mr-1" />
            New Agent
          </button>
        </div>
      </div>
      
      {/* Agents List */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {agentsData.map((agent) => (
          <div key={agent.id} className="card overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-200 dark:border-dark-700 flex items-center justify-between">
              <div className="flex items-center">
                <UserGroupIcon className={`h-5 w-5 mr-2 ${getTypeIconColor(agent.type)}`} />
                <h3 className="text-md font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
              </div>
              <span className={`badge ${getStatusBadgeClass(agent.status)}`}>
                {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
              </span>
            </div>
            
            <div className="px-4 py-3">
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                {agent.description}
              </p>
              
              <h4 className="text-xs font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-2">
                Capabilities
              </h4>
              <div className="flex flex-wrap gap-2 mb-3">
                {agent.capabilities.map((capability, index) => (
                  <span key={index} className="text-xs bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded-full">
                    {capability}
                  </span>
                ))}
              </div>
              
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Last active: {agent.lastActive}
              </div>
            </div>
            
            <div className="px-4 py-2 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-700 flex justify-between">
              <button className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center">
                <ChatBubbleLeftRightIcon className="h-4 w-4 mr-1" />
                Message
              </button>
              <button className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 flex items-center">
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Agents;