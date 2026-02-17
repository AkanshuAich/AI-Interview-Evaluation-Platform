/**
 * Authentication utilities for token management and validation.
 * 
 * Provides:
 * - Token storage in localStorage
 * - Token retrieval and validation
 * - Logout functionality
 */

const TOKEN_KEY = 'token';

/**
 * Store JWT token in localStorage
 */
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Retrieve JWT token from localStorage
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Remove JWT token from localStorage (logout)
 */
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

/**
 * Check if user is authenticated (has valid token)
 */
export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;
  
  try {
    // Decode JWT token to check expiration
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    return Date.now() < exp;
  } catch (error) {
    // Invalid token format
    return false;
  }
};

/**
 * Logout user (clear token and redirect to login)
 */
export const logout = () => {
  removeToken();
  window.location.href = '/login';
};
