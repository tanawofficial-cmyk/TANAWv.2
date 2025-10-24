import { Link } from "react-router-dom";
import logo from "../assets/TANAW-LOGO.png";

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-blue-900 text-gray-100">
      {/* Header */}
      <nav className="bg-gray-900/95 backdrop-blur-lg shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <Link to="/" className="flex items-center space-x-3 group">
              <img src={logo} alt="TANAW Logo" className="w-10 h-10 rounded-full object-cover ring-2 ring-blue-400/30" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                TANAW
              </span>
            </Link>
            <Link
              to="/"
              className="text-gray-300 hover:text-white transition-colors"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 md:p-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            About TANAW
          </h1>
          
          <div className="space-y-6 text-gray-300 leading-relaxed">
            <p className="text-lg">
              TANAW is an AI-powered analytics platform designed to help businesses transform raw data 
              into actionable insights through intelligent visualizations and automated analysis.
            </p>

            <h2 className="text-2xl font-bold text-white mt-8 mb-4">Our Mission</h2>
            <p>
              We believe that data analysis should be accessible to everyone, not just data scientists. 
              TANAW democratizes business intelligence by using artificial intelligence to automatically 
              understand your data and generate relevant analytics.
            </p>

            <h2 className="text-2xl font-bold text-white mt-8 mb-4">What We Do</h2>
            <ul className="space-y-3 ml-6">
              <li className="flex items-start">
                <span className="text-blue-400 mr-3">•</span>
                <span><strong className="text-white">Smart Domain Detection:</strong> Automatically identify whether your data is sales, inventory, finance, or customer-related</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-400 mr-3">•</span>
                <span><strong className="text-white">Intelligent Column Mapping:</strong> Use GPT-4o Mini to understand your column names and map them correctly</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-400 mr-3">•</span>
                <span><strong className="text-white">Automated Chart Generation:</strong> Create the perfect visualizations for your specific data type</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-400 mr-3">•</span>
                <span><strong className="text-white">Conversational Insights:</strong> Provide plain-language explanations of your data trends and patterns</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-400 mr-3">•</span>
                <span><strong className="text-white">Predictive Analytics:</strong> Forecast future trends using Facebook Prophet AI</span>
              </li>
            </ul>

            <h2 className="text-2xl font-bold text-white mt-8 mb-4">Technology</h2>
            <p>
              Built with cutting-edge technologies including React, Node.js, MongoDB, Python Flask, 
              OpenAI GPT-4o Mini, and Facebook Prophet, TANAW combines modern web development with 
              advanced AI capabilities to deliver a seamless analytics experience.
            </p>

            <div className="mt-8 pt-8 border-t border-white/10">
              <Link
                to="/register"
                className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-8 rounded-full font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
              >
                Start Using TANAW
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;

