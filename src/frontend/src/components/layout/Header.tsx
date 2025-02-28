import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store';
import { toggleSidebar, toggleTheme } from '../../store/slices/uiSlice';
import { 
  Bars3Icon, 
  SunIcon, 
  MoonIcon, 
  BellIcon, 
  UserCircleIcon 
} from '@heroicons/react/24/outline';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  const dispatch = useDispatch();
  const { theme, notifications } = useSelector((state: RootState) => state.ui);
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  const unreadNotifications = notifications.filter(n => !n.read).length;

  return (
    <header className="bg-white dark:bg-dark-800 shadow-sm z-10">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center">
          <button
            onClick={() => dispatch(toggleSidebar())}
            className="text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 focus:outline-none"
            aria-label="Toggle sidebar"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          
          <div className="ml-4 text-xl font-semibold text-gray-800 dark:text-white">
            AIDevOS
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Theme Toggle */}
          <button
            onClick={() => dispatch(toggleTheme())}
            className="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700 focus:outline-none"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? (
              <SunIcon className="h-5 w-5" />
            ) : (
              <MoonIcon className="h-5 w-5" />
            )}
          </button>
          
          {/* Notifications */}
          <Menu as="div" className="relative">
            <Menu.Button className="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700 focus:outline-none">
              <span className="sr-only">View notifications</span>
              <div className="relative">
                <BellIcon className="h-5 w-5" />
                {unreadNotifications > 0 && (
                  <span className="absolute -top-1 -right-1 bg-accent-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                    {unreadNotifications}
                  </span>
                )}
              </div>
            </Menu.Button>
            
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 mt-2 w-80 origin-top-right rounded-md bg-white dark:bg-dark-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none py-1 z-20">
                <div className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 border-b border-gray-200 dark:border-dark-600">
                  Notifications
                </div>
                
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                      No notifications
                    </div>
                  ) : (
                    notifications.slice(0, 5).map((notification) => (
                      <Menu.Item key={notification.id}>
                        <div className={`px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-dark-700 ${
                          !notification.read ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {notification.message}
                          </div>
                          <div className="text-gray-500 dark:text-gray-400 text-xs mt-1">
                            {new Date(notification.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </Menu.Item>
                    ))
                  )}
                </div>
                
                {notifications.length > 0 && (
                  <Link 
                    to="/notifications" 
                    className="block px-4 py-2 text-sm text-center text-primary-600 dark:text-primary-400 hover:bg-gray-50 dark:hover:bg-dark-700 border-t border-gray-200 dark:border-dark-600"
                  >
                    View all notifications
                  </Link>
                )}
              </Menu.Items>
            </Transition>
          </Menu>
          
          {/* User Menu */}
          <Menu as="div" className="relative">
            <Menu.Button className="p-1 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700 focus:outline-none">
              <span className="sr-only">Open user menu</span>
              <UserCircleIcon className="h-6 w-6" />
            </Menu.Button>
            
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 mt-2 w-48 origin-top-right rounded-md bg-white dark:bg-dark-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none py-1 z-20">
                {isAuthenticated ? (
                  <>
                    <div className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 border-b border-gray-200 dark:border-dark-600">
                      {user?.username}
                    </div>
                    
                    <Menu.Item>
                      {({ active }) => (
                        <Link
                          to="/profile"
                          className={`block px-4 py-2 text-sm ${
                            active ? 'bg-gray-100 dark:bg-dark-700 text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-200'
                          }`}
                        >
                          Profile
                        </Link>
                      )}
                    </Menu.Item>
                    <Menu.Item>
                      {({ active }) => (
                        <Link
                          to="/settings"
                          className={`block px-4 py-2 text-sm ${
                            active ? 'bg-gray-100 dark:bg-dark-700 text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-200'
                          }`}
                        >
                          Settings
                        </Link>
                      )}
                    </Menu.Item>
                    <Menu.Item>
                      {({ active }) => (
                        <button
                          className={`block w-full text-left px-4 py-2 text-sm ${
                            active ? 'bg-gray-100 dark:bg-dark-700 text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-200'
                          }`}
                        >
                          Sign out
                        </button>
                      )}
                    </Menu.Item>
                  </>
                ) : (
                  <>
                    <Menu.Item>
                      {({ active }) => (
                        <Link
                          to="/login"
                          className={`block px-4 py-2 text-sm ${
                            active ? 'bg-gray-100 dark:bg-dark-700 text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-200'
                          }`}
                        >
                          Sign in
                        </Link>
                      )}
                    </Menu.Item>
                  </>
                )}
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </header>
  );
};

export default Header;