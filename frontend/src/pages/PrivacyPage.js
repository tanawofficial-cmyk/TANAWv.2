import { Link } from "react-router-dom";
import logo from "../assets/TANAW-LOGO.png";

const PrivacyPage = () => {
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
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Privacy Policy
          </h1>
          <p className="text-sm text-gray-400 mb-8">Last Updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
          
          <div className="space-y-8 text-gray-300 leading-relaxed">
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Introduction</h2>
              <p>
                Welcome to TANAW ("we," "our," or "us"). We are committed to protecting your personal information 
                and your right to privacy. This Privacy Policy explains how we collect, use, and protect your data 
                when you use our AI-powered analytics platform.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Information We Collect</h2>
              <h3 className="text-xl font-semibold text-white mb-3">Account Information</h3>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Full name and business name</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Email address</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Password (encrypted)</span>
                </li>
              </ul>

              <h3 className="text-xl font-semibold text-white mb-3 mt-6">Data You Upload</h3>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>CSV files and their contents</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Analytics results and visualizations</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>User feedback and ratings</span>
                </li>
              </ul>

              <h3 className="text-xl font-semibold text-white mb-3 mt-6">Usage Information</h3>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Login times and session data</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Feature usage and analytics interactions</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>IP address and device information</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">How We Use Your Information</h2>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Provide Services:</strong> Process your data and generate analytics</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Improve Platform:</strong> Enhance AI accuracy and user experience</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Communication:</strong> Send important updates and notifications</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Security:</strong> Detect and prevent unauthorized access</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Data Security</h2>
              <p className="mb-4">
                We implement industry-standard security measures to protect your data:
              </p>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>End-to-end encryption for data transmission (HTTPS/TLS)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Encrypted storage in MongoDB with secure authentication</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>JWT tokens for secure session management</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Regular security audits and updates</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Third-Party Services</h2>
              <p className="mb-4">
                We use the following third-party services:
              </p>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">OpenAI GPT-4o Mini:</strong> For intelligent column mapping and insights generation</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">MongoDB Atlas:</strong> For secure data storage</span>
                </li>
              </ul>
              <p className="mt-4 text-sm text-gray-400">
                We ensure that all third-party services comply with data protection standards and do not share your data beyond what's necessary for service provision.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Your Rights</h2>
              <p className="mb-4">You have the right to:</p>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Access:</strong> Request a copy of your personal data</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Correction:</strong> Update inaccurate information</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Deletion:</strong> Request deletion of your account and data</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span><strong className="text-white">Portability:</strong> Export your data in a standard format</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Data Retention</h2>
              <p>
                We retain your data for as long as your account is active. If you delete your account, 
                we will permanently delete your personal information within 30 days, except where required 
                by law to retain certain records.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Contact Us</h2>
              <p className="mb-4">
                If you have any questions about this Privacy Policy or how we handle your data, please contact us:
              </p>
              <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                <p>
                  <strong className="text-white">Email:</strong>{' '}
                  <a href="mailto:tanawofficial@gmail.com" className="text-blue-400 hover:text-blue-300 transition-colors">
                    tanawofficial@gmail.com
                  </a>
                </p>
              </div>
            </div>

            <div className="pt-8 border-t border-white/10">
              <p className="text-sm text-gray-400">
                This Privacy Policy may be updated from time to time. We will notify you of any significant 
                changes by email or through our platform.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPage;

