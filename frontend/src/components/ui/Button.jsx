import React from 'react';

const Button = ({ children, onClick, variant = 'primary', className = '' }) => {
  const baseClasses = 'px-6 py-3 font-semibold rounded-md transition-all';
  const variants = {
    primary: 'text-white bg-indigo-600 hover:bg-indigo-500',
    secondary: 'text-gray-300 bg-gray-800 hover:bg-gray-700',
  };

  return (
    <button
      onClick={onClick}
      className={`${baseClasses} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;
