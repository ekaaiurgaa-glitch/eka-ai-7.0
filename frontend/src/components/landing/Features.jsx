import React from 'react';
import { Bot, Wrench, FileText, LayoutDashboard, BrainCircuit, ShieldCheck } from 'lucide-react';

const ai_models = [
  {
    "icon": Bot,
    "title": "AI Chat",
    "description": "Intelligent, domain-specific conversations for diagnostics and support."
  },
  {
    "icon": FileText,
    "title": "Job Card Automation",
    "description": "Generate detailed, accurate job cards from conversational inputs."
  },
  {
    "icon": Wrench,
    "title": "Repair Manuals",
    "description": "Instantly access and understand complex repair procedures with AI guidance."
  },
  {
    "icon": LayoutDashboard,
    "title": "Service Bulletins",
    "description": "Stay updated with the latest service bulletins and recall information."
  },
  {
    "icon": BrainCircuit,
    "title": "Predictive Maintenance",
    "description": "Anticipate vehicle issues before they happen with predictive analytics."
  },
  {
    "icon": ShieldCheck,
    "title": "Warranty & Claims",
    "description": "Streamline warranty claims and processing with AI-powered assistance."
  }
]

const Features = () => {
  return (
    <section id="features" className="py-20">
      <div className="container px-4 mx-auto">
        <h2 className="mb-12 text-4xl font-bold text-center text-white">Meet the EKA AI Agents</h2>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
          {ai_models.map((model, index) => (
            <div key={index} className="p-8 bg-gray-900 border border-gray-800 rounded-lg shadow-lg hover:shadow-indigo-500/20 transition-shadow">
              <div className="flex items-center justify-center w-12 h-12 mb-6 bg-gray-800 rounded-full">
                <model.icon className="w-6 h-6 text-indigo-400" />
              </div>
              <h3 className="mb-4 text-xl font-bold text-white">{model.title}</h3>
              <p className="text-gray-400">{model.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
