import { Link } from "react-router-dom";
import logo from "../assets/TANAW-LOGO.png";

const Footer = () => {
  return (
    <footer className="relative bg-gray-900/50 backdrop-blur-sm border-t border-white/10 py-12 md:py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-12 mb-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center space-x-3 mb-4 group">
              <img src={logo} alt="TANAW Logo" className="w-8 h-8 rounded-full object-cover group-hover:scale-110 transition-transform" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                TANAW
              </span>
            </Link>
            <p className="text-sm text-gray-400 mb-4">
              AI-powered analytics platform for intelligent data visualization and business insights.
            </p>
          </div>

          {/* Links */}
          {[
            {
              title: "Product",
              links: [
                { name: "Features", href: "/features" },
                { name: "How It Works", href: "/#how-it-works" },
                { name: "Analytics Types", href: "/#domains" },
                { name: "Updates", href: "/updates" }
              ]
            },
            {
              title: "Company",
              links: [
                { name: "About Us", href: "/about" },
                { name: "Contact", href: "/contact" },
                { name: "Privacy Policy", href: "/privacy" },
                { name: "Terms & Conditions", href: "/terms" }
              ]
            },
            {
              title: "Resources",
              links: [
                { name: "Documentation", href: "/docs" },
                { name: "Support", href: "/support" }
              ]
            }
          ].map((section, idx) => (
            <div key={idx}>
              <h4 className="text-white font-semibold mb-4">{section.title}</h4>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.name}>
                    <Link 
                      to={link.href} 
                      className="text-sm text-gray-400 hover:text-white transition-colors duration-200"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between">
          <p className="text-sm text-gray-400 mb-4 md:mb-0">
            &copy; {new Date().getFullYear()} TANAW. All rights reserved.
          </p>
          <div className="flex space-x-6 text-sm text-gray-400">
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

