import React from 'react';

const Deployments = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Deployments</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage and monitor deployments of Durable Objects
          </p>
        </div>
      </div>
      
      <div className="card p-6 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300">Deployments Panel</h2>
          <p className="mt-2 text-gray-500 dark:text-gray-400">This page is under construction</p>
        </div>
      </div>
    </div>
  );
};

export default Deployments;