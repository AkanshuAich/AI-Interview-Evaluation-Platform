/**
 * ProtectedRoute component for route guarding.
 * 
 * Redirects to login if user is not authenticated.
 */
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';

const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

export default ProtectedRoute;
