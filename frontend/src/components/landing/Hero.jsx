import React from 'react';

const Hero = () => {
  return (
    <section className="relative flex flex-col items-center justify-center min-h-screen pt-24 text-center">
      <div className="absolute inset-0 z-0 opacity-10">
        {/* Placeholder for a cool background graphic */}
      </div>
      <div className="relative z-10 flex flex-col items-center">
        <h1 className="text-6xl font-extrabold tracking-tighter text-white md:text-8xl">
          EKA AI
        </h1>
        <p className="mt-4 text-xl text-gray-400 md:text-2xl">
          An Automobile Intelligence
        </p>
        <div className="flex gap-4 mt-8">
          <a
            href="/login"
            className="px-8 py-3 font-semibold text-white bg-indigo-600 rounded-md hover:bg-indigo-500 transition-all"
          >
            Get Started
          </a>
          <a
            href="#features"
            className="px-8 py-3 font-semibold text-gray-300 bg-gray-800 rounded-md hover:bg-gray-700 transition-all"
          >
            Learn More
          </a>
        </div>
      </div>
    </section>
  );
};

export default Hero;
