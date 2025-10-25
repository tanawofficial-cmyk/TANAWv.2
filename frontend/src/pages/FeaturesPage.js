import { Link } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";

const FeaturesPage = () => {
  const features = [
    {
      category: "AI & Machine Learning",
      icon: "🤖",
      items: [
        {
          title: "GPT-4o Mini Integration",
          description: "Advanced column mapping and data interpretation using OpenAI's latest model",
          badge: "AI-Powered"
        },
        {
          title: "Prophet AI Forecasting",
          description: "Facebook Prophet for accurate time-series predictions with confidence intervals",
          badge: "ML Model"
        },
        {
          title: "Smart Domain Detection",
          description: "Automatically identifies Sales, Inventory, Finance, or Customer data domains",
          badge: "Intelligent"
        },
        {
          title: "Conversational Insights",
          description: "Plain-language explanations of trends, patterns, and actionable recommendations",
          badge: "GPT-Powered"
        }
      ]
    },
    {
      category: "Data Processing",
      icon: "⚙️",
      items: [
        {
          title: "Instant Upload & Analysis",
          description: "Upload CSV files up to 50MB and get analytics in seconds",
          badge: "Fast"
        },
        {
          title: "Automatic Data Cleaning",
          description: "Handles missing values, formats dates, and validates data types",
          badge: "Automated"
        },
        {
          title: "Intelligent Column Mapping",
          description: "AI understands your column names and maps them to standard formats",
          badge: "Smart"
        },
        {
          title: "Multi-Domain Support",
          description: "Analyzes Sales, Inventory, Finance, and Customer data in one platform",
          badge: "Versatile"
        }
      ]
    },
    {
      category: "Visualizations",
      icon: "📊",
      items: [
        {
          title: "15+ Chart Types",
          description: "Bar, line, pie charts, and advanced forecasts with Prophet AI",
          badge: "Rich"
        },
        {
          title: "Interactive Dashboards",
          description: "Responsive charts with tooltips, zoom, and smooth animations",
          badge: "Interactive"
        },
        {
          title: "Real-Time Updates",
          description: "Charts update instantly as you upload new datasets",
          badge: "Live"
        },
        {
          title: "Professional Design",
          description: "Beautiful gradients, glass morphism, and modern aesthetics",
          badge: "Beautiful"
        }
      ]
    },
    {
      category: "Analytics Capabilities",
      icon: "📈",
      items: [
        {
          title: "Sales Analytics",
          description: "Product performance, regional trends, revenue forecasts, and profit margins",
          badge: "Sales"
        },
        {
          title: "Inventory Analytics",
          description: "Stock levels, reorder status, turnover rates, and supplier performance",
          badge: "Inventory"
        },
        {
          title: "Financial Analytics",
          description: "Revenue vs expense trends, cash flow forecasts, and profit analysis",
          badge: "Finance"
        },
        {
          title: "Customer Analytics",
          description: "Segmentation, lifetime value, purchase patterns, and churn prediction",
          badge: "Customer"
        }
      ]
    },
    {
      category: "Security & Privacy",
      icon: "🔒",
      items: [
        {
          title: "End-to-End Encryption",
          description: "All data encrypted in transit (HTTPS/TLS) and at rest in MongoDB",
          badge: "Secure"
        },
        {
          title: "JWT Authentication",
          description: "Industry-standard token-based authentication for secure sessions",
          badge: "Protected"
        },
        {
          title: "Data Ownership",
          description: "You own your data - we never share it with third parties",
          badge: "Private"
        },
        {
          title: "Regular Audits",
          description: "Security reviews and updates to maintain highest standards",
          badge: "Monitored"
        }
      ]
    },
    {
      category: "User Experience",
      icon: "✨",
      items: [
        {
          title: "Fully Responsive",
          description: "Works perfectly on desktop, tablet, and mobile devices",
          badge: "Responsive"
        },
        {
          title: "Intuitive Interface",
          description: "Clean, modern design with drag-and-drop file uploads",
          badge: "Easy"
        },
        {
          title: "Export & Download",
          description: "Save charts as images and export insights as reports",
          badge: "Flexible"
        },
        {
          title: "Feedback System",
          description: "Rate your experience and provide feedback to improve TANAW",
          badge: "User-Focused"
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-blue-900 text-gray-100 flex flex-col">
      {/* Header */}
      <Header />

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Powerful Features
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Everything you need to transform your data into actionable business insights
          </p>
        </div>

        {/* Features Grid */}
        <div className="space-y-16">
          {features.map((category, idx) => (
            <div key={idx}>
              <div className="flex items-center space-x-3 mb-8">
                <span className="text-4xl">{category.icon}</span>
                <h2 className="text-3xl font-bold text-white">{category.category}</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {category.items.map((feature, featureIdx) => (
                  <div
                    key={featureIdx}
                    className="group p-6 bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-blue-400/50 rounded-2xl transition-all duration-300 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-xl font-bold text-white">{feature.title}</h3>
                      <span className="px-3 py-1 text-xs font-semibold bg-blue-500/20 text-blue-400 border border-blue-400/30 rounded-full">
                        {feature.badge}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center p-8 md:p-12 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-400/30 backdrop-blur-xl rounded-3xl">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Experience These Features?
          </h2>
          <p className="text-lg text-gray-300 mb-8">
            Start analyzing your business data with AI-powered insights
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-full text-base font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-blue-500/50"
            >
              Get Started Now
            </Link>
            <Link
              to="/docs"
              className="bg-white/10 backdrop-blur-sm border border-white/20 text-white px-8 py-3 rounded-full text-base font-semibold hover:bg-white/20 transition-all duration-300"
            >
              Read Documentation
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default FeaturesPage;

