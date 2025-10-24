import { Link } from "react-router-dom";
import { useState } from "react";
import logo from "../assets/TANAW-LOGO.png";

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Create email content
    const emailSubject = encodeURIComponent(`[TANAW Contact] ${formData.subject}`);
    const emailBody = encodeURIComponent(
      `Name: ${formData.name}\nEmail: ${formData.email}\n\nMessage:\n${formData.message}`
    );
    
    // Open default email client
    window.location.href = `mailto:tanawofficial@gmail.com?subject=${emailSubject}&body=${emailBody}`;
    
    // Reset form
    setTimeout(() => {
      setFormData({ name: "", email: "", subject: "", message: "" });
      alert("Your email client has been opened. Please send the email to complete your message.");
    }, 500);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

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
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Get in Touch
          </h1>
          <p className="text-lg text-gray-300">
            Have questions? We'd love to hear from you.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Contact Form */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Send us a message</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="your.email@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Subject
                </label>
                <input
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="How can we help?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Message
                </label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows="4"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  placeholder="Tell us more..."
                />
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
              >
                Send Message
              </button>
            </form>
          </div>

          {/* Contact Info */}
          <div className="space-y-6">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6">Contact Information</h2>
              <div className="space-y-4 text-gray-300">
                <div className="flex items-start space-x-3">
                  <span className="text-blue-400 text-xl">📧</span>
                  <div>
                    <p className="font-medium text-white">Email</p>
                    <a href="mailto:tanawofficial@gmail.com" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                      tanawofficial@gmail.com
                    </a>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <span className="text-blue-400 text-xl">📍</span>
                  <div>
                    <p className="font-medium text-white">Location</p>
                    <p className="text-sm">Batangas State University</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <span className="text-blue-400 text-xl">⏰</span>
                  <div>
                    <p className="font-medium text-white">Business Hours</p>
                    <p className="text-sm">Monday - Friday: 9:00 AM - 6:00 PM</p>
                    <p className="text-sm text-gray-400">Response time: Within 24 hours</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-400/30 backdrop-blur-sm rounded-2xl p-8">
              <h3 className="text-xl font-bold text-white mb-3">Need Help?</h3>
              <p className="text-gray-300 mb-4 text-sm">
                Check out our documentation or support resources for quick answers.
              </p>
              <div className="space-y-2">
                <Link
                  to="/docs"
                  className="block text-blue-400 hover:text-blue-300 text-sm"
                >
                  → Documentation
                </Link>
                <Link
                  to="/support"
                  className="block text-blue-400 hover:text-blue-300 text-sm"
                >
                  → Support Center
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;

