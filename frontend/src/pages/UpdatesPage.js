import { Link } from "react-router-dom";
import logo from "../assets/TANAW-LOGO.png";

const UpdatesPage = () => {
  const updates = [
    {
      date: "October 2024",
      version: "v1.5.0",
      badge: "Latest",
      badgeColor: "from-blue-500 to-purple-600",
      title: "Finance Domain Integration & Smart Routing",
      items: [
        "🎯 Merged Finance analytics into Sales domain for better accuracy",
        "🤖 Implemented smart domain detection with exclusive bonuses",
        "💰 Revenue calculation from Unit_Price × Sales_Volume",
        "📊 Enhanced chart generation with domain validators",
        "✨ Removed duplicate charts and improved routing logic"
      ]
    },
    {
      date: "October 2024",
      version: "v1.4.0",
      title: "Landing Page Overhaul & New Pages",
      items: [
        "🎨 Complete landing page redesign with animations",
        "📊 Added 3 animated sample charts (Bar, Line, Pie)",
        "✨ New slogan: 'See Beyond Numbers. Understand Your Story.'",
        "📚 Created comprehensive Documentation page",
        "💬 Added Support Center with 8 FAQs",
        "🔒 Implemented Privacy Policy and Terms of Service",
        "🤖 Updated to GPT-4o Mini for column mapping"
      ]
    },
    {
      date: "October 2024",
      version: "v1.3.0",
      title: "Admin Dashboard Enhancement",
      items: [
        "📊 Added Connectivity & Usage monitoring",
        "💬 Implemented User Feedback management tab",
        "📈 Real-time API usage metrics and stats",
        "🔌 Database connectivity status monitoring",
        "🎨 Professional UI redesign with TANAW logo",
        "🔄 Added responsive design for all screen sizes",
        "📊 User Management with dataset count per user"
      ]
    },
    {
      date: "September 2024",
      version: "v1.2.0",
      title: "User Dashboard Improvements",
      items: [
        "📱 Made dashboard fully responsive",
        "🎨 Enhanced header responsiveness",
        "📊 Multi-series line chart support",
        "🥧 Improved pie chart rendering with labels",
        "💬 Added feedback modal after every 3 uploads",
        "⭐ Star rating system for user experience",
        "🔄 Dynamic chart type detection"
      ]
    },
    {
      date: "September 2024",
      version: "v1.1.0",
      title: "Analytics Engine Upgrade",
      items: [
        "🤖 Integrated OpenAI GPT for column mapping",
        "🔮 Added Facebook Prophet AI for forecasting",
        "💬 Conversational insights generation",
        "📊 4 domain types: Sales, Inventory, Finance, Customer",
        "📈 15+ chart types with intelligent selection",
        "🎯 Smart domain detection algorithm",
        "✨ Automatic data cleaning and validation"
      ]
    },
    {
      date: "August 2024",
      version: "v1.0.0",
      badge: "Launch",
      badgeColor: "from-green-500 to-emerald-600",
      title: "TANAW Platform Launch",
      items: [
        "🚀 Initial release of TANAW platform",
        "📤 CSV file upload functionality",
        "📊 Basic chart generation (Bar, Line, Pie)",
        "👤 User authentication and authorization",
        "🔒 Secure data storage with MongoDB",
        "📱 Responsive web interface",
        "⚡ Real-time analytics processing"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-blue-900 text-gray-100">
      {/* Header */}
      <nav className="bg-gray-900/95 backdrop-blur-lg shadow-2xl sticky top-0 z-50">
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
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-400/30 rounded-full px-4 py-2 mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            <span className="text-sm text-blue-300 font-medium">Product Updates</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            What's New in TANAW
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Stay up to date with the latest features, improvements, and bug fixes
          </p>
        </div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-purple-500 to-pink-500 opacity-30"></div>

          {/* Updates */}
          <div className="space-y-12">
            {updates.map((update, idx) => (
              <div key={idx} className="relative pl-20">
                {/* Timeline Dot */}
                <div className="absolute left-6 top-6 w-5 h-5 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 border-4 border-gray-900"></div>

                {/* Update Card */}
                <div className="bg-gradient-to-br from-white/5 to-white/0 border border-white/10 rounded-2xl p-6 md:p-8 hover:border-blue-400/50 transition-all duration-300">
                  {/* Header */}
                  <div className="flex flex-wrap items-center gap-3 mb-4">
                    <span className="text-sm text-gray-400">{update.date}</span>
                    <span className="px-3 py-1 text-xs font-semibold bg-white/5 text-gray-300 border border-white/20 rounded-full">
                      {update.version}
                    </span>
                    {update.badge && (
                      <span className={`px-3 py-1 text-xs font-semibold bg-gradient-to-r ${update.badgeColor} text-white rounded-full`}>
                        {update.badge}
                      </span>
                    )}
                  </div>

                  {/* Title */}
                  <h2 className="text-2xl font-bold text-white mb-4">{update.title}</h2>

                  {/* Items */}
                  <ul className="space-y-2">
                    {update.items.map((item, itemIdx) => (
                      <li key={itemIdx} className="text-gray-300 text-sm leading-relaxed">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Coming Soon Section */}
        <div className="mt-16 p-8 md:p-12 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-400/30 backdrop-blur-xl rounded-3xl">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">🚀 Coming Soon</h2>
            <p className="text-gray-300 mb-6">We're constantly working to improve TANAW. Here's what's next:</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left max-w-3xl mx-auto">
              {[
                "📊 Real-time collaboration features",
                "🔗 API access for developers",
                "📱 Mobile app for iOS and Android",
                "🌐 Multi-language support",
                "🎨 Custom chart themes and branding",
                "🔄 Scheduled data refreshes"
              ].map((item, idx) => (
                <div key={idx} className="flex items-center space-x-3 p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300 text-sm">{item}</span>
                </div>
              ))}
            </div>

            <div className="mt-8 pt-8 border-t border-white/20">
              <p className="text-gray-400 text-sm mb-4">Have a feature request?</p>
              <Link
                to="/contact"
                className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-full text-sm font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
              >
                Send Feedback
              </Link>
            </div>
          </div>
        </div>

        {/* Newsletter Signup */}
        <div className="mt-12 text-center p-8 bg-white/5 border border-white/10 rounded-2xl">
          <h3 className="text-2xl font-bold text-white mb-3">Stay Updated</h3>
          <p className="text-gray-300 mb-6">Get notified about new features and updates</p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 max-w-md mx-auto">
            <a
              href="mailto:tanawofficial@gmail.com?subject=Subscribe%20to%20TANAW%20Updates&body=Please%20subscribe%20me%20to%20TANAW%20updates.%0A%0AMy%20email%3A%20"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 text-center"
            >
              Subscribe via Email
            </a>
          </div>
          <p className="text-xs text-gray-400 mt-4">Click to send a subscription request to tanawofficial@gmail.com</p>
        </div>
      </div>
    </div>
  );
};

export default UpdatesPage;

