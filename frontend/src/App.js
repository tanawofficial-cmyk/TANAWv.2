import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import DocumentationPage from "./pages/DocumentationPage";
import SupportPage from "./pages/SupportPage";
import PrivacyPage from "./pages/PrivacyPage";
import TermsPage from "./pages/TermsPage";
import FeaturesPage from "./pages/FeaturesPage";
import UpdatesPage from "./pages/UpdatesPage";


function App() {
  return (
    <Router>
      <Routes>
        {/* Default route = LandingPage */}
        <Route path="/" element={<LandingPage />} />

        {/* Auth routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/admin-login" element={<AdminLogin />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/register" element={<Register />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />

        {/* User Dashboard */}
        <Route path="/userDashboard" element={<Dashboard />} />

        {/* Admin Dashboard with nested routes */}
        <Route path="/admin/*" element={<AdminDashboard />} />

        {/* Product Pages */}
        <Route path="/features" element={<FeaturesPage />} />
        <Route path="/updates" element={<UpdatesPage />} />

        {/* Info Pages */}
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/docs" element={<DocumentationPage />} />
        <Route path="/support" element={<SupportPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        
        {/* API Reference (placeholder - points to docs) */}
        <Route path="/api" element={<DocumentationPage />} />
      </Routes>
    </Router>
  );
}

export default App;
