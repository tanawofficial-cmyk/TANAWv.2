// Protected Route component for admin-only pages
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const ProtectedRoute = ({ children }) => {
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const verifyAdminAccess = async () => {
      const token = localStorage.getItem('token');
      
      // No token = not logged in
      if (!token) {
        navigate('/admin-login', { replace: true });
        return;
      }

      try {
        // Try to fetch admin-only data to verify role
        const response = await api.get('/admin/stats');
        
        if (response && response.success) {
          // User is authorized admin
          setIsAuthorized(true);
          setIsChecking(false);
        } else {
          // Not authorized
          throw new Error('Unauthorized');
        }
      } catch (error) {
        console.error('❌ Admin access denied:', error);
        
        // Clear invalid session
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('role');
        
        setIsChecking(false);
        
        // Redirect to admin login
        navigate('/admin-login', { replace: true });
      }
    };

    verifyAdminAccess();
  }, [navigate]);

  // Show loading while checking
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying access...</p>
        </div>
      </div>
    );
  }

  // Only render children if authorized
  return isAuthorized ? children : null;
};

export default ProtectedRoute;

