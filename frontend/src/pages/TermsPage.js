import { Link } from "react-router-dom";
import logo from "../assets/TANAW-LOGO.png";

const TermsPage = () => {
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
            Terms of Service
          </h1>
          <p className="text-sm text-gray-400 mb-8">Last Updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
          
          <div className="space-y-8 text-gray-300 leading-relaxed">
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">1. Acceptance of Terms</h2>
              <p>
                By accessing and using TANAW's analytics platform, you agree to be bound by these Terms of Service. 
                If you do not agree to these terms, please do not use our services.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">2. Description of Service</h2>
              <p className="mb-4">
                TANAW provides an AI-powered analytics platform that:
              </p>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Automatically analyzes CSV data files</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Detects business domains (Sales, Inventory, Finance, Customer)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Generates intelligent visualizations and insights</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Provides predictive analytics using AI models</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">3. User Responsibilities</h2>
              <h3 className="text-xl font-semibold text-white mb-3">You agree to:</h3>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Provide accurate and complete registration information</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Maintain the security of your account credentials</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Only upload data that you own or have permission to use</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Comply with all applicable laws and regulations</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Not attempt to breach security or test vulnerabilities</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">4. Data Usage and Ownership</h2>
              <h3 className="text-xl font-semibold text-white mb-3">Your Data</h3>
              <ul className="space-y-2 ml-6 mb-4">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>You retain all rights to your uploaded data</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>We do not claim ownership of your data</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>We will not share your data with third parties without consent</span>
                </li>
              </ul>

              <h3 className="text-xl font-semibold text-white mb-3">Our Rights</h3>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>We may use anonymized, aggregated data to improve our services</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>All analytics results, charts, and insights generated remain available to you</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">5. Acceptable Use</h2>
              <h3 className="text-xl font-semibold text-white mb-3">You may NOT:</h3>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-red-400 mr-3">✗</span>
                  <span>Use the service for illegal activities</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-3">✗</span>
                  <span>Upload malicious files or code</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-3">✗</span>
                  <span>Attempt to reverse-engineer our AI models</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-3">✗</span>
                  <span>Share your account with unauthorized users</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-3">✗</span>
                  <span>Scrape or extract data from the platform</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-3">✗</span>
                  <span>Interfere with the service's operation</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">6. Service Limitations</h2>
              <p className="mb-4">TANAW is provided "as is" with the following limitations:</p>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Maximum file size: 50MB per upload</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Supported format: CSV only</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>AI analysis is probabilistic and may not be 100% accurate</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>We do not guarantee uninterrupted service availability</span>
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">7. Intellectual Property</h2>
              <p>
                TANAW's platform, including its AI models, algorithms, design, and branding, are protected 
                by intellectual property laws. You may not copy, modify, or distribute any part of our platform 
                without explicit permission.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">8. Termination</h2>
              <p className="mb-4">
                We reserve the right to suspend or terminate your account if you:
              </p>
              <ul className="space-y-2 ml-6">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Violate these Terms of Service</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Engage in fraudulent or abusive behavior</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">•</span>
                  <span>Fail to pay applicable fees (if any)</span>
                </li>
              </ul>
              <p className="mt-4">
                You may terminate your account at any time through your dashboard settings.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">9. Disclaimer of Warranties</h2>
              <p>
                TANAW is provided "as is" without warranties of any kind, express or implied. We do not guarantee 
                that the service will be error-free, secure, or continuously available. Use of AI-generated insights 
                is at your own risk, and we recommend verifying critical business decisions independently.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">10. Limitation of Liability</h2>
              <p>
                To the maximum extent permitted by law, TANAW shall not be liable for any indirect, incidental, 
                special, or consequential damages arising from your use of the service, including but not limited 
                to lost profits, data loss, or business interruption.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">11. Changes to Terms</h2>
              <p>
                We may update these Terms of Service from time to time. We will notify you of significant 
                changes via email or platform notification. Continued use of the service after changes 
                constitutes acceptance of the new terms.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white mb-4">12. Contact Information</h2>
              <p className="mb-4">
                For questions about these Terms of Service, please contact us:
              </p>
              <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                <p>
                  <strong className="text-white">Email:</strong>{' '}
                  <a href="mailto:tanawofficial@gmail.com" className="text-blue-400 hover:text-blue-300 transition-colors">
                    tanawofficial@gmail.com
                  </a>
                </p>
                <p className="mt-2">
                  <Link to="/contact" className="text-blue-400 hover:text-blue-300 transition-colors">
                    → Contact Form
                  </Link>
                </p>
              </div>
            </div>

            <div className="pt-8 border-t border-white/10">
              <p className="text-sm text-gray-400">
                By using TANAW, you acknowledge that you have read, understood, and agree to be bound by 
                these Terms of Service and our Privacy Policy.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsPage;

