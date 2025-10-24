import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import logo from "../assets/TANAW-LOGO.png";

const LandingPage = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="relative min-h-screen font-sans text-gray-100 bg-gradient-to-br from-gray-900 via-slate-900 to-blue-900 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-4000"></div>
      </div>

      {/* Navbar */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-gray-900/95 backdrop-blur-lg shadow-2xl' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            <div className="flex items-center space-x-3 group cursor-pointer">
              <div className="relative">
                <div className="absolute inset-0 bg-blue-500 rounded-full blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
                <img src={logo} alt="TANAW Logo" className="relative w-8 h-8 md:w-10 md:h-10 rounded-full object-cover ring-2 ring-blue-400/30" />
              </div>
              <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                TANAW
              </span>
            </div>
            <div className="flex items-center space-x-3 md:space-x-6">
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

      {/* Hero Section */}
      <header className="relative pt-32 pb-20 md:pt-40 md:pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-400/30 rounded-full px-4 py-2 mb-8 backdrop-blur-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              <span className="text-xs md:text-sm text-blue-300 font-medium">AI-Powered Analytics Platform</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6 md:mb-8">
              <span className="block text-white">Transform Your Data</span>
              <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Into Actionable Insights
              </span>
            </h1>

            <p className="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto mb-10 md:mb-12 leading-relaxed">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-300 via-purple-300 to-pink-300 font-semibold">
                See Beyond Numbers. Understand Your Story.
              </span>
              <br />
              <span className="text-gray-400 text-base md:text-lg mt-2 block">
                Transform raw CSV data into intelligent business insights with AI-powered analytics
              </span>
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link
                to="/register"
                className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-full text-base md:text-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-blue-500/50"
              >
                Get Started Now
              </Link>
              <a
                href="#how-it-works"
                className="w-full sm:w-auto bg-white/10 backdrop-blur-sm border border-white/20 text-white py-3 px-6 rounded-full text-base md:text-lg font-semibold hover:bg-white/20 transition-all duration-300"
              >
                See How It Works
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 md:gap-8 max-w-3xl mx-auto">
              {[
                { value: "4", label: "Domain Types" },
                { value: "15+", label: "Chart Types" },
                { value: "AI", label: "Powered" }
              ].map((stat, idx) => (
                <div key={idx} className="text-center p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
                  <div className="text-2xl md:text-3xl font-bold text-white mb-1">{stat.value}</div>
                  <div className="text-xs md:text-sm text-gray-400">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* How It Works Section */}
      <section id="how-it-works" className="relative py-20 md:py-32 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-transparent to-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 md:mb-20">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 md:mb-6">
              How TANAW Works
            </h2>
            <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto">
              Three simple steps to turn your data into insights
            </p>
          </div>

          {/* Process Steps */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 mb-16">
            {[
              {
                step: "1",
                icon: "📤",
                title: "Upload Your Data",
                description: "Simply drag and drop your CSV file. TANAW supports sales, inventory, finance, and customer datasets with automatic data validation and cleaning."
              },
              {
                step: "2",
                icon: "🤖",
                title: "AI Analysis",
                description: "Our AI engine automatically maps your columns, detects your business domain, and intelligently selects the most relevant analytics for your data type."
              },
              {
                step: "3",
                icon: "📊",
                title: "Get Insights",
                description: "View beautiful visualizations with conversational insights, actionable recommendations, and predictive forecasts powered by Prophet AI."
              }
            ].map((step, idx) => (
              <div
                key={idx}
                className="relative group"
              >
                {/* Step Number */}
                <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg z-10">
                  {step.step}
                </div>
                
                <div className="p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-blue-400/50 backdrop-blur-sm transition-all duration-300 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20 h-full">
                  <div className="text-5xl mb-4 transform group-hover:scale-110 transition-transform duration-300">
                    {step.icon}
                  </div>
                  <h3 className="text-xl md:text-2xl font-bold text-white mb-3">{step.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Domain Detection Section */}
      <section id="domains" className="relative py-20 md:py-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              Smart Domain Detection
            </h2>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              TANAW automatically recognizes your data type and generates relevant analytics
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
            {[
              {
                icon: "💰",
                domain: "Sales & Finance",
                description: "Revenue analysis, profit margins, expense tracking, cash flow forecasting, and financial performance metrics"
              },
              {
                icon: "📦",
                domain: "Inventory Management",
                description: "Stock level monitoring, reorder alerts, inventory turnover, supplier performance, and warehouse optimization"
              },
              {
                icon: "👥",
                domain: "Customer Analytics",
                description: "Customer segmentation, lifetime value analysis, purchase patterns, churn prediction, and satisfaction trends"
              },
              {
                icon: "🔀",
                domain: "Mixed Domains",
                description: "Comprehensive analytics combining multiple business aspects for holistic insights and cross-domain correlations"
              }
            ].map((item, idx) => (
              <div
                key={idx}
                className="group p-6 md:p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-blue-400/50 backdrop-blur-sm transition-all duration-300 hover:transform hover:scale-105"
              >
                <div className="flex items-start space-x-4">
                  <div className="text-4xl flex-shrink-0 transform group-hover:scale-110 transition-transform">
                    {item.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2">{item.domain}</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">{item.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Sample Charts Showcase */}
      <section className="relative py-20 md:py-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              See It In Action
            </h2>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              Real examples of TANAW's intelligent visualizations
            </p>
          </div>

          {/* Animated Chart Samples */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {/* Sample Bar Chart */}
            <div className="group relative p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-blue-400/50 backdrop-blur-sm transition-all duration-500 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20">
              <div className="text-sm font-semibold text-blue-400 mb-4">📊 Product Performance</div>
              <div className="space-y-3">
                {[
                  { label: 'Product A', value: 85, color: 'from-blue-500 to-blue-600', delay: '0s' },
                  { label: 'Product B', value: 65, color: 'from-purple-500 to-purple-600', delay: '0.1s' },
                  { label: 'Product C', value: 45, color: 'from-pink-500 to-pink-600', delay: '0.2s' },
                  { label: 'Product D', value: 30, color: 'from-indigo-500 to-indigo-600', delay: '0.3s' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center space-x-3">
                    <span className="text-xs text-gray-400 w-16 text-right">{item.label}</span>
                    <div className="flex-1 h-8 bg-white/5 rounded-lg overflow-hidden">
                      <div 
                        className={`h-full bg-gradient-to-r ${item.color} animate-bar-grow transition-all duration-1000`}
                        style={{ 
                          width: `${item.value}%`,
                          animationDelay: item.delay
                        }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-500 w-8">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sample Line Chart */}
            <div className="group relative p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-purple-400/50 backdrop-blur-sm transition-all duration-500 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20">
              <div className="text-sm font-semibold text-purple-400 mb-4">📈 Revenue Trend</div>
              <div className="h-32 flex items-end justify-between space-x-1">
                {[30, 45, 38, 52, 48, 65, 58, 72, 68, 85].map((height, idx) => (
                  <div key={idx} className="flex-1 flex flex-col items-center">
                    <div 
                      className="w-full bg-gradient-to-t from-purple-500 to-transparent rounded-t-lg animate-line-grow transition-all duration-1000"
                      style={{ 
                        height: `${height}%`,
                        animationDelay: `${idx * 0.1}s`
                      }}
                    ></div>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex justify-between text-xs text-gray-500">
                <span>Jan</span>
                <span>Mar</span>
                <span>May</span>
                <span>Jul</span>
                <span>Sep</span>
              </div>
            </div>

            {/* Sample Pie Chart */}
            <div className="group relative p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-pink-400/50 backdrop-blur-sm transition-all duration-500 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-pink-500/20">
              <div className="text-sm font-semibold text-pink-400 mb-4">🎯 Market Share</div>
              <div className="flex items-center justify-center h-32">
                <div className="relative w-24 h-24">
                  <div className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 animate-spin-slow"></div>
                  <div className="absolute inset-0 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 clip-quarter animate-spin-slow-reverse" style={{ animationDelay: '0.5s' }}></div>
                  <div className="absolute inset-0 rounded-full bg-gradient-to-br from-pink-500 to-pink-600 clip-half animate-pulse-slow"></div>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-blue-600"></div>
                  <span className="text-gray-400">Sales 40%</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-purple-600"></div>
                  <span className="text-gray-400">Finance 35%</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-gradient-to-r from-pink-500 to-pink-600"></div>
                  <span className="text-gray-400">Other 25%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Charts Types Section */}
      <section className="relative py-20 md:py-32 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-transparent to-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              Intelligent Visualizations
            </h2>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              TANAW generates the perfect charts for your data automatically
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                type: "📊 Bar Charts",
                charts: ["Product Performance", "Regional Sales", "Stock Levels", "Profit Margins"]
              },
              {
                type: "📈 Line Charts",
                charts: ["Sales Trends", "Revenue vs Expense", "Inventory Turnover", "Customer Growth"]
              },
              {
                type: "🔮 Forecasts",
                charts: ["Sales Predictions", "Demand Forecasting", "Cash Flow Projection", "Stock Reorder Planning"]
              }
            ].map((category, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-blue-400/50 backdrop-blur-sm transition-all duration-300"
              >
                <h3 className="text-xl font-bold text-white mb-4">{category.type}</h3>
                <ul className="space-y-2">
                  {category.charts.map((chart, i) => (
                    <li key={i} className="flex items-center text-gray-400 text-sm">
                      <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mr-3"></span>
                      {chart}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Additional Features */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-400/30 backdrop-blur-sm">
              <div className="text-3xl mb-3">🧠</div>
              <h3 className="text-lg font-bold text-white mb-2">Conversational Insights</h3>
              <p className="text-gray-400 text-sm">
                Every chart comes with AI-generated analysis written in plain language, explaining trends, patterns, and actionable recommendations.
              </p>
            </div>
            <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-400/30 backdrop-blur-sm">
              <div className="text-3xl mb-3">🎨</div>
              <h3 className="text-lg font-bold text-white mb-2">Beautiful by Default</h3>
              <p className="text-gray-400 text-sm">
                Modern, professional charts with smooth animations, interactive tooltips, and responsive design that looks great on any device.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-20 md:py-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              Powerful Features
            </h2>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              Everything you need to analyze and visualize your business data
            </p>
          </div>

          {/* Feature Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {[
              {
                icon: "🤖",
                title: "GPT-4o Mini Powered",
                description: "Intelligent column detection and mapping using OpenAI's latest GPT-4o Mini for accurate data interpretation"
              },
              {
                icon: "🔮",
                title: "Prophet AI Forecasting",
                description: "Facebook Prophet integration for advanced time-series predictions with confidence intervals"
              },
              {
                icon: "⚡",
                title: "Instant Analysis",
                description: "Upload CSV files and get analytics in seconds with automatic data cleaning and validation"
              },
              {
                icon: "📱",
                title: "Fully Responsive",
                description: "Beautiful dashboards that work perfectly on desktop, tablet, and mobile devices"
              },
              {
                icon: "🔒",
                title: "Secure & Private",
                description: "Your data is encrypted and secure. JWT authentication and MongoDB security best practices"
              },
              {
                icon: "📥",
                title: "Download Reports",
                description: "Export your charts, insights, and data in multiple formats for presentations and reports"
              }
            ].map((feature, idx) => (
              <div
                key={idx}
                className="group p-6 md:p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-blue-400/50 backdrop-blur-sm transition-all duration-300 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20"
              >
                <div className="text-4xl md:text-5xl mb-4 transform group-hover:scale-110 transition-transform duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-xl md:text-2xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 md:py-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="p-8 md:p-12 rounded-3xl bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-400/30 backdrop-blur-xl">
            <img src={logo} alt="TANAW Logo" className="w-16 h-16 md:w-20 md:h-20 rounded-full object-cover mx-auto mb-6 ring-4 ring-blue-400/30" />
            
            <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-400/30 rounded-full px-4 py-2 mb-6">
              <span className="text-xs md:text-sm text-blue-300 font-medium uppercase tracking-wider">See Data Differently</span>
            </div>

            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 md:mb-6">
              Ready to Transform Your Data?
            </h2>
            <p className="text-lg md:text-xl text-gray-300 mb-8 md:mb-10 max-w-2xl mx-auto">
              Start analyzing your business data with AI-powered insights and intelligent visualizations.
            </p>
            <Link
              to="/register"
              className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-8 rounded-full text-base font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-blue-500/50"
            >
              Get Started Now
            </Link>
            <p className="mt-6 text-sm text-gray-400">AI-powered analytics • Instant insights</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative bg-gray-900/50 backdrop-blur-sm border-t border-white/10 py-12 md:py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-12 mb-12">
            {/* Brand */}
            <div className="md:col-span-1">
              <div className="flex items-center space-x-3 mb-4">
                <img src={logo} alt="TANAW Logo" className="w-8 h-8 rounded-full object-cover" />
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  TANAW
                </span>
              </div>
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
                  { name: "Privacy Policy", href: "/privacy" }
                ]
              },
              {
                title: "Resources",
                links: [
                  { name: "Documentation", href: "/docs" },
                  { name: "Support", href: "/support" },
                  { name: "API Reference", href: "/api" }
                ]
              }
            ].map((section, idx) => (
              <div key={idx}>
                <h4 className="text-white font-semibold mb-4">{section.title}</h4>
                <ul className="space-y-2">
                  {section.links.map((link) => (
                    <li key={link.name}>
                      <Link to={link.href} className="text-sm text-gray-400 hover:text-white transition-colors duration-200">
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

      {/* Custom CSS for animations */}
      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        .animate-blob {
          animation: blob 20s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        
        /* Chart Animations */
        @keyframes bar-grow {
          from {
            width: 0%;
            opacity: 0.5;
          }
          to {
            opacity: 1;
          }
        }
        .animate-bar-grow {
          animation: bar-grow 1.5s ease-out forwards;
        }
        
        @keyframes line-grow {
          from {
            height: 0%;
            opacity: 0.5;
          }
          to {
            opacity: 1;
          }
        }
        .animate-line-grow {
          animation: line-grow 1.5s ease-out forwards;
        }
        
        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
        .animate-spin-slow {
          animation: spin-slow 20s linear infinite;
        }
        
        @keyframes spin-slow-reverse {
          from {
            transform: rotate(360deg);
          }
          to {
            transform: rotate(0deg);
          }
        }
        .animate-spin-slow-reverse {
          animation: spin-slow-reverse 15s linear infinite;
        }
        
        @keyframes pulse-slow {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.7;
          }
        }
        .animate-pulse-slow {
          animation: pulse-slow 3s ease-in-out infinite;
        }
        
        .clip-quarter {
          clip-path: polygon(50% 50%, 100% 0, 100% 100%);
        }
        
        .clip-half {
          clip-path: polygon(50% 50%, 0 0, 0 100%, 50% 100%);
        }
        
        /* Floating animation for cards */
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }
        .hover\:animate-float:hover {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
