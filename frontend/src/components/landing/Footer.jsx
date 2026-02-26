import React from 'react';

const Footer = () => {
  return (
    <footer className="py-12 bg-gray-900 border-t border-gray-800">
      <div className="container px-4 mx-auto text-center">
        <p className="text-sm text-gray-500">
          © {new Date().getFullYear()} eka-ai.in. All rights reserved.
        </p>
        <div className="flex justify-center gap-6 mt-4">
          <a href="/terms" className="text-sm text-gray-400 hover:text-white transition-colors">
            Terms of Service
          </a>
          <a href="/privacy" className="text-sm text-gray-400 hover:text-white transition-colors">
            Privacy Policy
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
