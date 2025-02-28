import React, { ReactNode } from 'react';

interface CardProps {
  title?: string | ReactNode;
  titleAction?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
  bordered?: boolean;
}

const Card: React.FC<CardProps> = ({
  title,
  titleAction,
  footer,
  children,
  className = '',
  noPadding = false,
  bordered = true,
}) => {
  const baseClasses = 'card bg-white dark:bg-dark-800 rounded-lg shadow-soft overflow-hidden';
  const borderClasses = bordered ? 'border border-gray-200 dark:border-dark-700' : '';
  const combinedClasses = `${baseClasses} ${borderClasses} ${className}`;

  return (
    <div className={combinedClasses}>
      {title && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-dark-700 flex items-center justify-between">
          {typeof title === 'string' ? (
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
          ) : (
            title
          )}
          {titleAction && <div>{titleAction}</div>}
        </div>
      )}
      
      <div className={noPadding ? '' : 'p-4'}>
        {children}
      </div>
      
      {footer && (
        <div className="px-4 py-3 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-700">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;