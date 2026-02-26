import React from 'react';

const Card = ({ children, className = '' }) => {
  return (
    <div
      className={`p-8 bg-gray-900 border border-gray-800 rounded-lg shadow-lg hover:shadow-indigo-500/20 transition-shadow ${className}`}
    >
      {children}
    </div>
  );
};

export default Card;
