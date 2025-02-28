import React from 'react';
import { Link } from 'react-router-dom';
import { HomeIcon } from '@heroicons/react/24/outline';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center px-4">
      <div className="text-9xl font-bold text-primary-400 dark:text-primary-600">404</div>
      
      <h1 className="mt-4 text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
        Page not found
      </h1>
      
      <p className="mt-2 text-lg text-gray-600 dark:text-gray-400">
        Sorry, we couldn't find the page you're looking for.
      </p>
      
      <div className="mt-8">
        <Link
          to="/"
          className="btn btn-primary inline-flex items-center"
        >
          <HomeIcon className="h-5 w-5 mr-2" />
          Return to home
        </Link>
      </div>
    </div>
  );
};

export default NotFound;