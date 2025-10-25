import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import logo from "../assets/TANAW-LOGO.png";

const Header = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav className={`sticky top-0 z-50 transition-all duration-300 ${scrolled ? 'bg-gray-900/95 backdrop-blur-lg shadow-2xl' : 'bg-gray-900/95 backdrop-blur-lg shadow-xl'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 rounded-full blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
              <img src={logo} alt="TANAW Logo" className="relative w-8 h-8 md:w-10 md:h-10 rounded-full object-cover ring-2 ring-blue-400/30" />
            </div>
            <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              TANAW
            </span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center space-x-3 md:space-x-6">
            <Link
              to="/features"
              className="text-sm md:text-base text-gray-300 font-medium hover:text-white transition-colors duration-300 hidden sm:inline-block"
            >
              Features
            </Link>
            <Link
              to="/docs"
              className="text-sm md:text-base text-gray-300 font-medium hover:text-white transition-colors duration-300 hidden sm:inline-block"
            >
              Docs
            </Link>
            <Link
              to="/support"
              className="text-sm md:text-base text-gray-300 font-medium hover:text-white transition-colors duration-300 hidden sm:inline-block"
            >
              Support
            </Link>
            <Link
              to="/login"
              className="text-sm md:text-base text-gray-300 font-medium hover:text-white transition-colors duration-300"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-3 md:px-4 py-1.5 md:py-2 rounded-full font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-blue-500/50 text-sm md:text-base"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Header;

