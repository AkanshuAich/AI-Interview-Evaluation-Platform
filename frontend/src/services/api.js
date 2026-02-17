/**
 * API client service for backend communication.
 * 
 * Provides:
 * - Axios instance with base URL configuration
 * - Request interceptor for JWT token injection
 * - Response interceptor for error handling
 * - API functions for all backend endpoints
 */
import axios from 'axios';

// Create axios instance with base URL from environment
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add JWT token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      // Handle 401 Unauthorized - clear token and redirect to login
      if (status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      
      // Return error with message
      return Promise.reject({
        status,
        message: data.detail || 'An error occurred',
      });
    } else if (error.request) {
      // Request made but no response received
      return Promise.reject({
        status: 0,
        message: 'Network error. Please check your connection.',
      });
    } else {
      // Something else happened
      return Promise.reject({
        status: 0,
        message: error.message || 'An unexpected error occurred',
      });
    }
  }
);

// Authentication API
export const authAPI = {
  register: (username, email, password) =>
    api.post('/api/auth/register', { username, email, password }),
  
  login: (username, password) =>
    api.post('/api/auth/login', { username, password }),
  
  getCurrentUser: () =>
    api.get('/api/auth/me'),
};

// Interview API
export const interviewAPI = {
  createInterview: (role, num_questions) =>
    api.post('/api/interviews', { role, num_questions }),
  
  listInterviews: () =>
    api.get('/api/interviews'),
  
  getInterview: (interviewId) =>
    api.get(`/api/interviews/${interviewId}`),
};

// Answer API
export const answerAPI = {
  submitAnswer: (interview_id, question_id, answer_text) =>
    api.post('/api/answers', { interview_id, question_id, answer_text }),
  
  getAnswerStatus: (answerId) =>
    api.get(`/api/answers/${answerId}/status`),
};

// Report API
export const reportAPI = {
  getInterviewReport: (interviewId) =>
    api.get(`/api/reports/${interviewId}`),
};

export default api;
