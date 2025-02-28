import React from 'react';
import { 
  UserGroupIcon, 
  ServerIcon, 
  ShieldCheckIcon, 
  ChartBarIcon,
  CodeBracketSquareIcon
} from '@heroicons/react/24/outline';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data for demo
const agentsData = [
  { id: '1', name: 'PM Agent', status: 'active', type: 'PM', lastActive: '2 minutes ago' },
  { id: '2', name: 'Backend Agent', status: 'active', type: 'Backend', lastActive: '5 minutes ago' },
  { id: '3', name: 'Frontend Agent', status: 'active', type: 'Frontend', lastActive: 'Just now' },
  { id: '4', name: 'DevOps Agent', status: 'idle', type: 'DevOps', lastActive: '15 minutes ago' },
  { id: '5', name: 'QA Agent', status: 'idle', type: 'QA', lastActive: '30 minutes ago' },
];

const deploymentData = [
  { id: '1', name: 'User Management Service', status: 'running', uptime: '5d 12h 30m', version: 'v1.2.3' },
  { id: '2', name: 'Authentication Service', status: 'running', uptime: '5d 12h 30m', version: 'v1.0.1' },
  { id: '3', name: 'Data Processing Service', status: 'running', uptime: '3d 8h 45m', version: 'v0.9.5' },
];

const performanceData = [
  { name: '00:00', value: 2400 },
  { name: '03:00', value: 1398 },
  { name: '06:00', value: 9800 },
  { name: '09:00', value: 3908 },
  { name: '12:00', value: 4800 },
  { name: '15:00', value: 3800 },
  { name: '18:00', value: 4300 },
  { name: '21:00', value: 2400 },
];

const stats = [
  { name: 'Active Agents', value: '5', icon: UserGroupIcon, color: 'bg-blue-500' },
  { name: 'Running Services', value: '12', icon: ServerIcon, color: 'bg-green-500' },
  { name: 'System Health', value: '98%', icon: ShieldCheckIcon, color: 'bg-yellow-500' },
  { name: 'Modules Generated', value: '42', icon: CodeBracketSquareIcon, color: 'bg-purple-500' },
];

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <div className="flex gap-2">
          <button className="btn btn-outline">
            Refresh
          </button>
          <button className="btn btn-primary">
            New Deployment
          </button>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card p-4">
            <div className="flex items-start">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <div className="ml-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{stat.value}</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">{stat.name}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Performance Chart */}
      <div className="card p-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Performance</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={performanceData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-dark-600" />
              <XAxis dataKey="name" className="text-xs text-gray-500 dark:text-gray-400" />
              <YAxis className="text-xs text-gray-500 dark:text-gray-400" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  border: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 2px 15px -3px rgba(0, 0, 0, 0.07)',
                }}
              />
              <Area type="monotone" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Agents */}
        <div className="card">
          <div className="px-4 py-3 border-b border-gray-200 dark:border-dark-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Active Agents</h2>
            <span className="badge badge-blue">5 Agents</span>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-dark-700">
            {agentsData.map((agent) => (
              <div key={agent.id} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <UserGroupIcon className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{agent.name}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Last active: {agent.lastActive}</p>
                    </div>
                  </div>
                  <span className={`badge ${
                    agent.status === 'active' ? 'badge-green' : 'badge-yellow'
                  }`}>
                    {agent.status === 'active' ? 'Active' : 'Idle'}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="px-4 py-2 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-700">
            <button className="w-full text-center text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300">
              View All Agents
            </button>
          </div>
        </div>
        
        {/* Deployments */}
        <div className="card">
          <div className="px-4 py-3 border-b border-gray-200 dark:border-dark-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Active Deployments</h2>
            <span className="badge badge-green">3 Running</span>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-dark-700">
            {deploymentData.map((deploy) => (
              <div key={deploy.id} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <ServerIcon className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{deploy.name}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {deploy.version} • Uptime: {deploy.uptime}
                      </p>
                    </div>
                  </div>
                  <span className="badge badge-green">
                    Running
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="px-4 py-2 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-700">
            <button className="w-full text-center text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300">
              View All Deployments
            </button>
          </div>
        </div>
      </div>
      
      {/* Recent Activity */}
      <div className="card">
        <div className="px-4 py-3 border-b border-gray-200 dark:border-dark-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Activity</h2>
        </div>
        <div className="px-4 py-2 divide-y divide-gray-200 dark:divide-dark-700">
          <div className="py-3">
            <div className="flex">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  System monitoring detected increased CPU usage
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  10 minutes ago
                </p>
              </div>
            </div>
          </div>
          
          <div className="py-3">
            <div className="flex">
              <div className="flex-shrink-0">
                <ServerIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Data Processing Service was automatically scaled up
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  25 minutes ago
                </p>
              </div>
            </div>
          </div>
          
          <div className="py-3">
            <div className="flex">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Backend Agent generated new API endpoint for user authentication
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  1 hour ago
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="px-4 py-2 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-700">
          <button className="w-full text-center text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300">
            View All Activity
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;