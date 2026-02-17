/**
 * Main App component with routing configuration.
 * 
 * Routes:
 * - /login: Login page (public)
 * - /dashboard: Dashboard page (protected)
 * - /interview/:id: Interview page (protected)
 * - /report/:id: Report page (protected)
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import InterviewPage from './pages/InterviewPage';
import ReportPage from './pages/ReportPage';
import ProtectedRoute from './components/ProtectedRoute';
import { isAuthenticated } from './utils/auth';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            isAuthenticated() ? <Navigate to="/dashboard" replace /> : <LoginPage />
          }
        />
        
        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/interview/:id"
          element={
            <ProtectedRoute>
              <InterviewPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/report/:id"
          element={
            <ProtectedRoute>
              <ReportPage />
            </ProtectedRoute>
          }
        />
        
        {/* Default Route */}
        <Route
          path="/"
          element={
            <Navigate to={isAuthenticated() ? '/dashboard' : '/login'} replace />
          }
        />
        
        {/* 404 Route */}
        <Route
          path="*"
          element={
            <Navigate to={isAuthenticated() ? '/dashboard' : '/login'} replace />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
