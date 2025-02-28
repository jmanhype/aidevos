import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-white dark:bg-dark-800 border-t border-gray-200 dark:border-dark-700 px-4 py-3">
      <div className="container mx-auto flex flex-col md:flex-row justify-between items-center text-sm text-gray-500 dark:text-gray-400">
        <div className="mb-2 md:mb-0">
          <span>&copy; {currentYear} AIDevOS. All rights reserved.</span>
        </div>
        
        <div className="flex space-x-6">
          <a 
            href="https://github.com/yourusername/aidevos" 
            target="_blank" 
            rel="noopener noreferrer"
            className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            GitHub
          </a>
          <a 
            href="/docs" 
            className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            Documentation
          </a>
          <a 
            href="/api" 
            className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            API
          </a>
          <a 
            href="/privacy" 
            className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            Privacy
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;