import { useSelector } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { RootState } from '../../store';
import {
  HomeIcon,
  UsersIcon,
  ServerIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  CodeBracketIcon,
  DocumentTextIcon,
  BoltIcon,
  CommandLineIcon,
} from '@heroicons/react/24/outline';

interface NavItem {
  name: string;
  to: string;
  icon: (props: React.ComponentProps<'svg'>) => JSX.Element;
}

const mainNavItems: NavItem[] = [
  { name: 'Dashboard', to: '/', icon: HomeIcon },
  { name: 'Agents', to: '/agents', icon: UsersIcon },
  { name: 'Deployments', to: '/deployments', icon: ServerIcon },
  { name: 'Monitoring', to: '/monitoring', icon: ChartBarIcon },
  { name: 'Code Generation', to: '/code', icon: CodeBracketIcon },
];

const secondaryNavItems: NavItem[] = [
  { name: 'Projects', to: '/projects', icon: DocumentTextIcon },
  { name: 'Automation', to: '/automation', icon: BoltIcon },
  { name: 'CLI', to: '/cli', icon: CommandLineIcon },
  { name: 'Settings', to: '/settings', icon: Cog6ToothIcon },
];

const Sidebar = () => {
  const { sidebarOpen } = useSelector((state: RootState) => state.ui);

  if (!sidebarOpen) {
    return null;
  }

  return (
    <aside className="fixed inset-y-0 left-0 z-20 flex-shrink-0 w-64 bg-white dark:bg-dark-800 shadow-md transform transition-transform duration-300 md:translate-x-0">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center justify-center h-16 border-b border-gray-200 dark:border-dark-700">
          <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
            AIDevOS
          </span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-6 overflow-y-auto">
          <div>
            <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Main
            </h3>
            <div className="mt-2 space-y-1">
              {mainNavItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.to}
                  className={({ isActive }) => `
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                    ${isActive
                      ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700'
                    }
                  `}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 transition-colors
                      ${
                        location.pathname === item.to
                          ? 'text-primary-500 dark:text-primary-400'
                          : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'
                      }
                    `}
                    aria-hidden="true"
                  />
                  {item.name}
                </NavLink>
              ))}
            </div>
          </div>

          <div>
            <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Tools
            </h3>
            <div className="mt-2 space-y-1">
              {secondaryNavItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.to}
                  className={({ isActive }) => `
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                    ${isActive
                      ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700'
                    }
                  `}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 transition-colors
                      ${
                        location.pathname === item.to
                          ? 'text-primary-500 dark:text-primary-400'
                          : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'
                      }
                    `}
                    aria-hidden="true"
                  />
                  {item.name}
                </NavLink>
              ))}
            </div>
          </div>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-dark-700">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 dark:bg-primary-900/30">
                <UsersIcon className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">AI Agent System</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Version 0.1.0</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;