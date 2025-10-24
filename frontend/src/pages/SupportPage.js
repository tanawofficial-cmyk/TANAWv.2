import { Link } from "react-router-dom";
import { useState } from "react";
import logo from "../assets/TANAW-LOGO.png";

const SupportPage = () => {
  const [openFaq, setOpenFaq] = useState(null);

  const faqs = [
    {
      question: "How do I upload a CSV file?",
      answer: "Simply drag and drop your CSV file into the upload area on your dashboard, or click to browse your files. The file will be automatically analyzed once uploaded."
    },
    {
      question: "What file size limits apply?",
      answer: "Currently, TANAW supports CSV files up to 50MB in size. If your file is larger, consider splitting it into smaller chunks or filtering the data before upload."
    },
    {
      question: "Which domains does TANAW support?",
      answer: "TANAW supports four main domains: Sales & Finance, Inventory Management, Customer Analytics, and Mixed Domains. The system automatically detects your data type."
    },
    {
      question: "How accurate are the AI forecasts?",
      answer: "TANAW uses Facebook Prophet AI, which provides high accuracy for time-series predictions. Forecasts include confidence intervals to show the range of possible outcomes."
    },
    {
      question: "Can I download my charts and insights?",
      answer: "Yes! You can download individual charts or export complete reports from your dashboard. Charts can be saved as images, and insights can be exported as PDF."
    },
    {
      question: "How is my data secured?",
      answer: "All data is encrypted in transit and at rest. We use JWT authentication, MongoDB security best practices, and never share your data with third parties."
    },
    {
      question: "What happens if domain detection is wrong?",
      answer: "Our AI is highly accurate, but if you believe the detection is incorrect, you can contact support. We recommend using clear column names (e.g., 'Revenue' instead of 'Amount') for best results."
    },
    {
      question: "How long does analysis take?",
      answer: "Most analyses complete within 10-30 seconds, depending on file size and complexity. You'll see a progress indicator while TANAW processes your data."
    }
  ];

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
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            How Can We Help?
          </h1>
          <p className="text-lg text-gray-300">
            Find answers to common questions or reach out to our support team
          </p>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <Link
            to="/docs"
            className="group p-6 bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-blue-400/50 rounded-2xl transition-all duration-300 hover:transform hover:scale-105"
          >
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-xl font-bold text-white mb-2">Documentation</h3>
            <p className="text-gray-400 text-sm">Complete guides and tutorials</p>
          </Link>

          <Link
            to="/contact"
            className="group p-6 bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-purple-400/50 rounded-2xl transition-all duration-300 hover:transform hover:scale-105"
          >
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-xl font-bold text-white mb-2">Contact Us</h3>
            <p className="text-gray-400 text-sm">Get in touch with our team</p>
          </Link>

          <a
            href="mailto:tanawofficial@gmail.com"
            className="group p-6 bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-pink-400/50 rounded-2xl transition-all duration-300 hover:transform hover:scale-105 block"
          >
            <div className="text-4xl mb-4">📧</div>
            <h3 className="text-xl font-bold text-white mb-2">Email Support</h3>
            <p className="text-blue-400 hover:text-blue-300 text-sm transition-colors">tanawofficial@gmail.com</p>
          </a>
        </div>

        {/* FAQ Section */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-white mb-8">Frequently Asked Questions</h2>
          
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-white/5 border border-white/10 rounded-xl overflow-hidden transition-all duration-300"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-white/5 transition-colors"
                >
                  <span className="text-white font-semibold pr-8">{faq.question}</span>
                  <span className="text-blue-400 text-2xl flex-shrink-0">
                    {openFaq === index ? '−' : '+'}
                  </span>
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-4 text-gray-300 text-sm leading-relaxed border-t border-white/10 pt-4">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Support Hours */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/30 rounded-xl">
            <h3 className="text-xl font-bold text-white mb-4">Support Hours</h3>
            <div className="space-y-2 text-gray-300">
              <p><strong className="text-white">Monday - Friday:</strong> 9:00 AM - 6:00 PM</p>
              <p><strong className="text-white">Weekend:</strong> Limited support</p>
              <p className="text-sm text-gray-400 mt-4">
                Average response time: <span className="text-blue-400 font-semibold">Within 24 hours</span>
              </p>
            </div>
          </div>

          <div className="p-6 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-400/30 rounded-xl">
            <h3 className="text-xl font-bold text-white mb-4">Emergency Issues</h3>
            <p className="text-gray-300 mb-4">
              For critical issues affecting your business operations:
            </p>
            <Link
              to="/contact"
              className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
            >
              Report Critical Issue
            </Link>
          </div>
        </div>

        {/* Still Need Help */}
        <div className="mt-12 text-center p-8 bg-white/5 border border-white/10 rounded-2xl">
          <h3 className="text-2xl font-bold text-white mb-4">Still Need Help?</h3>
          <p className="text-gray-300 mb-6">
            Our support team is here to assist you with any questions or issues
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/contact"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-full font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
            >
              Contact Support
            </Link>
            <Link
              to="/docs"
              className="bg-white/10 backdrop-blur-sm border border-white/20 text-white px-8 py-3 rounded-full font-semibold hover:bg-white/20 transition-all duration-300"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupportPage;

