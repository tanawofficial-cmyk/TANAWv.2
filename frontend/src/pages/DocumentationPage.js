import { Link } from "react-router-dom";
import { useState } from "react";
import logo from "../assets/TANAW-LOGO.png";

const DocumentationPage = () => {
  const [activeSection, setActiveSection] = useState("getting-started");

  const sections = [
    { id: "getting-started", title: "Getting Started", icon: "🚀" },
    { id: "upload-data", title: "Uploading Data", icon: "📤" },
    { id: "domains", title: "Domain Types", icon: "🎯" },
    { id: "charts", title: "Chart Types", icon: "📊" },
    { id: "insights", title: "AI Insights", icon: "🧠" },
    { id: "troubleshooting", title: "Troubleshooting", icon: "🔧" }
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <div className="lg:w-64 flex-shrink-0">
            <div className="sticky top-24 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">Documentation</h3>
              <nav className="space-y-2">
                {sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-all duration-200 ${
                      activeSection === section.id
                        ? 'bg-blue-500/20 text-blue-400 border border-blue-400/30'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <span className="mr-2">{section.icon}</span>
                    {section.title}
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 md:p-12">
              {activeSection === "getting-started" && (
                <div className="space-y-6">
                  <h1 className="text-4xl font-bold text-white mb-4">🚀 Getting Started with TANAW</h1>
                  <p className="text-gray-300 leading-relaxed">
                    Welcome to TANAW! This guide will help you get started with transforming your data into actionable insights.
                  </p>

                  <h2 className="text-2xl font-bold text-white mt-8 mb-4">What is TANAW?</h2>
                  <p className="text-gray-300 leading-relaxed">
                    TANAW is an AI-powered analytics platform that automatically analyzes your CSV files, detects your business domain, 
                    and generates intelligent visualizations with conversational insights.
                  </p>

                  <h2 className="text-2xl font-bold text-white mt-8 mb-4">Quick Start</h2>
                  <ol className="space-y-4 text-gray-300 ml-6">
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">1.</span>
                      <span><strong className="text-white">Create an Account:</strong> Sign up with your email and business name</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">2.</span>
                      <span><strong className="text-white">Upload Your Data:</strong> Drag and drop your CSV file (max 50MB)</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">3.</span>
                      <span><strong className="text-white">Get Insights:</strong> TANAW automatically generates charts and insights</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">4.</span>
                      <span><strong className="text-white">Explore Analytics:</strong> Review your dashboard and download reports</span>
                    </li>
                  </ol>

                  <div className="mt-8 p-6 bg-blue-500/10 border border-blue-400/30 rounded-xl">
                    <h3 className="text-lg font-bold text-blue-400 mb-2">💡 Pro Tip</h3>
                    <p className="text-gray-300 text-sm">
                      Make sure your CSV has clear column names and at least 10 rows of data for the best results!
                    </p>
                  </div>
                </div>
              )}

              {activeSection === "upload-data" && (
                <div className="space-y-6">
                  <h1 className="text-4xl font-bold text-white mb-4">📤 Uploading Data</h1>
                  
                  <h2 className="text-2xl font-bold text-white mt-8 mb-4">Supported File Format</h2>
                  <p className="text-gray-300 leading-relaxed">
                    TANAW currently supports CSV (Comma-Separated Values) files. Make sure your file:
                  </p>
                  <ul className="space-y-2 text-gray-300 ml-6">
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span>Has a header row with column names</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span>Contains at least 10 rows of data</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span>Is less than 50MB in size</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span>Uses UTF-8 encoding</span>
                    </li>
                  </ul>

                  <h2 className="text-2xl font-bold text-white mt-8 mb-4">Column Requirements</h2>
                  <p className="text-gray-300 leading-relaxed mb-4">
                    For best results, include these types of columns:
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                      <h3 className="text-white font-semibold mb-2">📅 Date/Time</h3>
                      <p className="text-sm text-gray-400">Transaction dates, timestamps</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                      <h3 className="text-white font-semibold mb-2">💰 Monetary Values</h3>
                      <p className="text-sm text-gray-400">Revenue, sales, prices, costs</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                      <h3 className="text-white font-semibold mb-2">📦 Products/Items</h3>
                      <p className="text-sm text-gray-400">Product names, SKUs, categories</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                      <h3 className="text-white font-semibold mb-2">🔢 Quantities</h3>
                      <p className="text-sm text-gray-400">Stock levels, sales volume, units</p>
                    </div>
                  </div>

                  <h2 className="text-2xl font-bold text-white mt-8 mb-4">Upload Process</h2>
                  <ol className="space-y-3 text-gray-300 ml-6">
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">1.</span>
                      <span>Click the upload area or drag your CSV file</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">2.</span>
                      <span>TANAW validates your file format and structure</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">3.</span>
                      <span>AI analyzes your columns and detects domain</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 font-bold mr-3">4.</span>
                      <span>Charts and insights are generated automatically</span>
                    </li>
                  </ol>
                </div>
              )}

              {activeSection === "domains" && (
                <div className="space-y-6">
                  <h1 className="text-4xl font-bold text-white mb-4">🎯 Domain Types</h1>
                  <p className="text-gray-300 leading-relaxed">
                    TANAW automatically detects which business domain your data belongs to and generates relevant analytics.
                  </p>

                  <div className="space-y-6 mt-8">
                    <div className="p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/30 rounded-xl">
                      <h3 className="text-2xl font-bold text-white mb-3">💰 Sales & Finance</h3>
                      <p className="text-gray-300 mb-4">
                        Detected when your data contains revenue, expenses, sales amounts, or financial transactions.
                      </p>
                      <p className="text-sm text-gray-400 mb-2"><strong className="text-white">Key Columns:</strong> Revenue, Sales, Expense, Budget, Transaction Amount</p>
                      <p className="text-sm text-gray-400"><strong className="text-white">Charts Generated:</strong> Product Performance, Revenue Trends, Profit Margins, Cash Flow Forecasts</p>
                    </div>

                    <div className="p-6 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-400/30 rounded-xl">
                      <h3 className="text-2xl font-bold text-white mb-3">📦 Inventory Management</h3>
                      <p className="text-gray-300 mb-4">
                        Detected when your data contains stock levels, reorder points, or supplier information.
                      </p>
                      <p className="text-sm text-gray-400 mb-2"><strong className="text-white">Key Columns:</strong> Stock Level, Reorder Point, Warehouse, Supplier, SKU</p>
                      <p className="text-sm text-gray-400"><strong className="text-white">Charts Generated:</strong> Stock Levels, Reorder Status, Inventory Turnover, Supplier Performance</p>
                    </div>

                    <div className="p-6 bg-gradient-to-r from-pink-500/10 to-indigo-500/10 border border-pink-400/30 rounded-xl">
                      <h3 className="text-2xl font-bold text-white mb-3">👥 Customer Analytics</h3>
                      <p className="text-gray-300 mb-4">
                        Detected when your data contains customer information, segments, or lifetime values.
                      </p>
                      <p className="text-sm text-gray-400 mb-2"><strong className="text-white">Key Columns:</strong> Customer ID, Segment, Lifetime Value, Purchase Frequency</p>
                      <p className="text-sm text-gray-400"><strong className="text-white">Charts Generated:</strong> Customer Segmentation, Purchase Patterns, Churn Analysis, LTV Analysis</p>
                    </div>

                    <div className="p-6 bg-gradient-to-r from-indigo-500/10 to-blue-500/10 border border-indigo-400/30 rounded-xl">
                      <h3 className="text-2xl font-bold text-white mb-3">🔀 Mixed Domains</h3>
                      <p className="text-gray-300 mb-4">
                        Detected when your data spans multiple business areas, providing comprehensive analytics.
                      </p>
                      <p className="text-sm text-gray-400 mb-2"><strong className="text-white">Key Feature:</strong> Combines analytics from multiple domains</p>
                      <p className="text-sm text-gray-400"><strong className="text-white">Charts Generated:</strong> All relevant charts from detected domains</p>
                    </div>
                  </div>
                </div>
              )}

              {activeSection === "charts" && (
                <div className="space-y-6">
                  <h1 className="text-4xl font-bold text-white mb-4">📊 Chart Types</h1>
                  <p className="text-gray-300 leading-relaxed">
                    TANAW generates various chart types based on your data and domain.
                  </p>

                  <div className="space-y-6 mt-8">
                    <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                      <h3 className="text-xl font-bold text-white mb-3">📊 Bar Charts</h3>
                      <p className="text-gray-300 mb-3">Compare values across categories</p>
                      <ul className="space-y-2 text-sm text-gray-400 ml-6">
                        <li>• Product Performance Comparison</li>
                        <li>• Regional Sales Distribution</li>
                        <li>• Stock Level Overview</li>
                        <li>• Profit Margin Analysis</li>
                      </ul>
                    </div>

                    <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                      <h3 className="text-xl font-bold text-white mb-3">📈 Line Charts</h3>
                      <p className="text-gray-300 mb-3">Track trends over time</p>
                      <ul className="space-y-2 text-sm text-gray-400 ml-6">
                        <li>• Sales Trend Analysis</li>
                        <li>• Revenue vs Expense Tracking</li>
                        <li>• Inventory Turnover Trends</li>
                        <li>• Customer Growth Over Time</li>
                      </ul>
                    </div>

                    <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                      <h3 className="text-xl font-bold text-white mb-3">🥧 Pie Charts</h3>
                      <p className="text-gray-300 mb-3">Show proportional distributions</p>
                      <ul className="space-y-2 text-sm text-gray-400 ml-6">
                        <li>• Market Share Distribution</li>
                        <li>• Customer Segmentation</li>
                        <li>• Expense Breakdown</li>
                        <li>• Category Analysis</li>
                      </ul>
                    </div>

                    <div className="p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/30 rounded-xl">
                      <h3 className="text-xl font-bold text-white mb-3">🔮 Forecast Charts</h3>
                      <p className="text-gray-300 mb-3">Predict future trends using Prophet AI</p>
                      <ul className="space-y-2 text-sm text-gray-400 ml-6">
                        <li>• Sales Forecasting (30 days ahead)</li>
                        <li>• Demand Prediction</li>
                        <li>• Cash Flow Projection</li>
                        <li>• Stock Reorder Planning</li>
                      </ul>
                      <p className="text-xs text-blue-400 mt-4">
                        ✨ Powered by Facebook Prophet AI with confidence intervals
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeSection === "insights" && (
                <div className="space-y-6">
                  <h1 className="text-4xl font-bold text-white mb-4">🧠 AI-Powered Insights</h1>
                  <p className="text-gray-300 leading-relaxed">
                    Every chart comes with conversational insights written in plain language.
                  </p>

                  <h2 className="text-2xl font-bold text-white mt-8 mb-4">What Are Conversational Insights?</h2>
                  <p className="text-gray-300 leading-relaxed">
                    Using GPT-4o Mini, TANAW analyzes your charts and generates human-friendly explanations that include:
                  </p>
                  <ul className="space-y-3 text-gray-300 ml-6 mt-4">
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span><strong className="text-white">Trend Analysis:</strong> What's happening in your data</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span><strong className="text-white">Pattern Recognition:</strong> Identifying peaks, dips, and anomalies</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span><strong className="text-white">Actionable Recommendations:</strong> Specific steps you can take</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-400 mr-3">•</span>
                      <span><strong className="text-white">Business Impact:</strong> How it affects your bottom line</span>
                    </li>
                  </ul>

                  <div className="mt-8 p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/30 rounded-xl">
                    <h3 className="text-lg font-bold text-blue-400 mb-3">Example Insight</h3>
                    <p className="text-gray-300 text-sm italic mb-4">
                      "Your sales peaked at ₱195,000 on January 15th, showing a 23% increase from the previous week. 
                      This surge coincides with your marketing campaign. Consider replicating this strategy in Q2 to 
                      maintain momentum. The forecast suggests continued growth if current trends persist."
                    </p>
                    <p className="text-xs text-gray-400">
                      💡 Insights are personalized to your business and data patterns
                    </p>
                  </div>
                </div>
              )}

              {activeSection === "troubleshooting" && (
                <div className="space-y-6">
                  <h1 className="text-4xl font-bold text-white mb-4">🔧 Troubleshooting</h1>
                  
                  <h2 className="text-2xl font-bold text-white mt-8 mb-4">Common Issues</h2>
                  
                  <div className="space-y-4">
                    <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                      <h3 className="text-white font-semibold mb-2">❌ File Upload Failed</h3>
                      <p className="text-sm text-gray-400 mb-2"><strong>Possible Causes:</strong></p>
                      <ul className="text-sm text-gray-400 ml-6 space-y-1">
                        <li>• File size exceeds 50MB</li>
                        <li>• File is not in CSV format</li>
                        <li>• Network connection issues</li>
                      </ul>
                      <p className="text-sm text-blue-400 mt-2"><strong>Solution:</strong> Compress your file, check format, or try again</p>
                    </div>

                    <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                      <h3 className="text-white font-semibold mb-2">❌ No Charts Generated</h3>
                      <p className="text-sm text-gray-400 mb-2"><strong>Possible Causes:</strong></p>
                      <ul className="text-sm text-gray-400 ml-6 space-y-1">
                        <li>• Too few rows (need at least 10)</li>
                        <li>• Missing required columns</li>
                        <li>• Data format issues</li>
                      </ul>
                      <p className="text-sm text-blue-400 mt-2"><strong>Solution:</strong> Ensure proper column names and enough data rows</p>
                    </div>

                    <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                      <h3 className="text-white font-semibold mb-2">❌ Incorrect Domain Detection</h3>
                      <p className="text-sm text-gray-400 mb-2"><strong>Possible Causes:</strong></p>
                      <ul className="text-sm text-gray-400 ml-6 space-y-1">
                        <li>• Ambiguous column names</li>
                        <li>• Mixed data types</li>
                        <li>• Insufficient domain indicators</li>
                      </ul>
                      <p className="text-sm text-blue-400 mt-2"><strong>Solution:</strong> Use clearer column names (e.g., "Revenue" instead of "Amount")</p>
                    </div>
                  </div>

                  <div className="mt-8 p-6 bg-blue-500/10 border border-blue-400/30 rounded-xl">
                    <h3 className="text-lg font-bold text-blue-400 mb-2">Need More Help?</h3>
                    <p className="text-gray-300 text-sm mb-4">
                      If you're still experiencing issues, please contact our support team.
                    </p>
                    <Link
                      to="/contact"
                      className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
                    >
                      Contact Support
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentationPage;

