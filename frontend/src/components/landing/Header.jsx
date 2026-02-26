import React from 'react';
import { Sparkles } from 'lucide-react';

const Header = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 bg-black bg-opacity-50 backdrop-blur-md">
      <div className="flex items-center gap-2">
        <Sparkles className="text-accent" size={20} />
        <h1 className="text-lg font-bold tracking-tighter">eka-ai.in</h1>
      </div>
      <nav className="flex items-center gap-6 text-sm">
        <a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a>
        <a href="#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</a>
        <a href="/login" className="px-4 py-2 text-sm font-semibold text-white bg-gray-800 rounded-md hover:bg-gray-700 transition-colors">
          Login
        </a>
      </nav>
    </header>
  );
};

export default Header;
