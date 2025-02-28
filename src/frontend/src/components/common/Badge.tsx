import React, { ReactNode } from 'react';

export type BadgeVariant = 'default' | 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info';
export type BadgeSize = 'sm' | 'md' | 'lg';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  className?: string;
  dot?: boolean;
}

const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
  dot = false,
}) => {
  // Base classes
  const baseClasses = 'inline-flex items-center font-medium';
  
  // Size classes
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs rounded-full',
    md: 'px-2.5 py-0.5 text-xs rounded-full',
    lg: 'px-3 py-1 text-sm rounded-full',
  };
  
  // Variant classes
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    primary: 'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300',
    secondary: 'bg-secondary-100 text-secondary-800 dark:bg-secondary-900/30 dark:text-secondary-300',
    success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    danger: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  };
  
  // Dot color classes
  const dotColorClasses = {
    default: 'bg-gray-500 dark:bg-gray-400',
    primary: 'bg-primary-500 dark:bg-primary-400',
    secondary: 'bg-secondary-500 dark:bg-secondary-400',
    success: 'bg-green-500 dark:bg-green-400',
    danger: 'bg-red-500 dark:bg-red-400',
    warning: 'bg-yellow-500 dark:bg-yellow-400',
    info: 'bg-blue-500 dark:bg-blue-400',
  };
  
  const badgeClasses = [
    baseClasses,
    sizeClasses[size],
    variantClasses[variant],
    className,
  ].join(' ');

  return (
    <span className={badgeClasses}>
      {dot && (
        <span 
          className={`mr-1.5 h-2 w-2 rounded-full ${dotColorClasses[variant]}`} 
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
};

export default Badge;