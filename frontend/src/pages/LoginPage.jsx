/**
 * LoginPage component for user authentication and registration.
 *
 * Features:
 * - Login and registration forms with smooth transition
 * - Form validation (required fields, min lengths)
 * - JWT token storage on successful login/registration
 * - Redirect to dashboard on success
 * - Error message display on failure
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import { setToken } from '../utils/auth';

const LoginPage = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = () => {
    const newErrors = {};
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }
    if (!isLogin) {
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Email is invalid';
      }
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    if (!isLogin && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
    if (apiError) setApiError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setIsLoading(true);
    setApiError('');
    try {
      if (isLogin) {
        const response = await authAPI.login(formData.username, formData.password);
        setToken(response.data.access_token);
        navigate('/dashboard');
      } else {
        const response = await authAPI.register(formData.username, formData.email, formData.password);
        setToken(response.data.access_token);
        navigate('/dashboard');
      }
    } catch (error) {
      setApiError(error.message || `${isLogin ? 'Login' : 'Registration'} failed. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setFormData({ username: '', email: '', password: '', confirmPassword: '' });
    setErrors({});
    setApiError('');
  };

  const styles = `
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');
    .lp-root *, .lp-root *::before, .lp-root *::after { box-sizing: border-box; }
    .lp-root {
      min-height: 100vh; display: grid; grid-template-columns: 1fr 1fr;
      font-family: 'DM Sans', sans-serif; background: #060912; overflow: hidden;
    }
    .lp-hero {
      position: relative; display: flex; flex-direction: column;
      justify-content: space-between; padding: 3rem; overflow: hidden;
      background: linear-gradient(145deg, #0d1528 0%, #060c1a 60%, #060912 100%);
    }
    .lp-hero::before {
      content: ''; position: absolute; top: -150px; left: -150px;
      width: 550px; height: 550px;
      background: radial-gradient(circle, rgba(99,179,237,0.12) 0%, transparent 65%);
      border-radius: 50%; pointer-events: none;
    }
    .lp-hero::after {
      content: ''; position: absolute; bottom: -100px; right: -80px;
      width: 420px; height: 420px;
      background: radial-gradient(circle, rgba(246,173,85,0.07) 0%, transparent 65%);
      border-radius: 50%; pointer-events: none;
    }
    .lp-brand { display: flex; align-items: center; gap: .75rem; z-index: 1; position: relative; }
    .lp-brand-icon {
      width: 40px; height: 40px; background: linear-gradient(135deg, #63b3ed, #3182ce);
      border-radius: 10px; display: flex; align-items: center; justify-content: center;
      font-size: 1.2rem; box-shadow: 0 4px 16px rgba(66,153,225,.35);
    }
    .lp-brand-name {
      font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700;
      color: #e2e8f0; letter-spacing: -.02em;
    }
    .lp-hero-body { z-index: 1; position: relative; }
    .lp-eyebrow {
      font-size: .68rem; font-weight: 500; letter-spacing: .18em; text-transform: uppercase;
      color: #63b3ed; margin-bottom: 1.25rem; display: flex; align-items: center; gap: .5rem;
    }
    .lp-eyebrow::before {
      content: ''; display: inline-block; width: 22px; height: 2px;
      background: #63b3ed; border-radius: 2px;
    }
    .lp-headline {
      font-family: 'Syne', sans-serif; font-size: clamp(2.2rem, 3.2vw, 3.1rem);
      font-weight: 800; line-height: 1.05; letter-spacing: -.045em; color: #f7fafc;
      margin-bottom: 1.4rem;
    }
    .lp-headline .acc { color: #63b3ed; }
    .lp-subtext {
      font-size: .95rem; font-weight: 300; color: #4a5568; line-height: 1.75;
      max-width: 360px; margin-bottom: 2.25rem;
    }
    .lp-stats { display: grid; grid-template-columns: repeat(3,1fr); gap: .875rem; margin-bottom: 2rem; }
    .lp-stat {
      background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.06);
      border-radius: 12px; padding: .875rem .75rem; text-align: center;
    }
    .lp-stat-n {
      font-family: 'Syne', sans-serif; font-size: 1.45rem; font-weight: 800;
      color: #e2e8f0; letter-spacing: -.03em;
    }
    .lp-stat-l { font-size: .68rem; color: #4a5568; margin-top: .2rem; letter-spacing: .03em; }
    .lp-testi {
      z-index: 1; position: relative;
      background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06);
      border-radius: 14px; padding: 1.25rem; backdrop-filter: blur(10px);
    }
    .lp-testi-q { font-size: .85rem; color: #718096; font-style: italic; line-height: 1.7; margin-bottom: .875rem; }
    .lp-testi-author { display: flex; align-items: center; gap: .625rem; }
    .lp-avatar {
      width: 32px; height: 32px; border-radius: 50%;
      background: linear-gradient(135deg, #63b3ed, #3182ce);
      display: flex; align-items: center; justify-content: center;
      font-size: .7rem; font-weight: 700; color: white; flex-shrink: 0;
    }
    .lp-author-name { font-size: .78rem; font-weight: 500; color: #cbd5e0; }
    .lp-author-role { font-size: .68rem; color: #4a5568; }
    .lp-stars { color: #f6ad55; font-size: .65rem; letter-spacing: .05em; margin-top: 1px; }

    /* Right panel */
    .lp-panel {
      display: flex; align-items: center; justify-content: center;
      padding: 3rem 4rem; background: #090e1d;
      border-left: 1px solid rgba(255,255,255,.05);
    }
    .lp-box { width: 100%; max-width: 390px; }
    .lp-seg {
      display: flex; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.07);
      border-radius: 10px; padding: 4px; margin-bottom: 2rem;
    }
    .lp-seg-btn {
      flex: 1; padding: .55rem; border: none; border-radius: 7px;
      font-family: 'DM Sans', sans-serif; font-size: .8rem; font-weight: 500;
      cursor: pointer; transition: all .2s ease; background: transparent; color: #4a5568;
    }
    .lp-seg-btn.on { background: #1a2744; color: #63b3ed; box-shadow: 0 2px 8px rgba(0,0,0,.35); }
    .lp-title {
      font-family: 'Syne', sans-serif; font-size: 1.65rem; font-weight: 800;
      color: #e2e8f0; letter-spacing: -.04em; line-height: 1.1; margin-bottom: .35rem;
    }
    .lp-sub { font-size: .85rem; color: #4a5568; font-weight: 300; margin-bottom: 1.75rem; }
    .lp-err {
      background: rgba(245,101,101,.08); border: 1px solid rgba(245,101,101,.25);
      border-radius: 8px; padding: .7rem .9rem; font-size: .8rem; color: #fc8181;
      margin-bottom: 1.25rem; display: flex; align-items: flex-start; gap: .5rem;
    }
    .lp-fields { display: flex; flex-direction: column; gap: .8rem; margin-bottom: 1.4rem; }
    .lp-field { display: flex; flex-direction: column; gap: .3rem; }
    .lp-label { font-size: .7rem; font-weight: 500; color: #4a5568; letter-spacing: .07em; text-transform: uppercase; }
    .lp-input {
      width: 100%; padding: .75rem 1rem; background: rgba(255,255,255,.04);
      border: 1px solid rgba(255,255,255,.08); border-radius: 10px;
      font-family: 'DM Sans', sans-serif; font-size: .9rem; color: #e2e8f0;
      outline: none; transition: border-color .2s, box-shadow .2s, background .2s;
      -webkit-appearance: none; appearance: none;
    }
    .lp-input::placeholder { color: #2d3748; }
    .lp-input:focus {
      border-color: rgba(99,179,237,.45); background: rgba(255,255,255,.06);
      box-shadow: 0 0 0 3px rgba(99,179,237,.07);
    }
    .lp-input.lp-err-inp { border-color: rgba(245,101,101,.45); }
    .lp-ferr { font-size: .7rem; color: #fc8181; }
    .lp-btn {
      width: 100%; padding: .9rem; border: none; border-radius: 10px;
      font-family: 'Syne', sans-serif; font-size: .95rem; font-weight: 700;
      letter-spacing: -.01em; cursor: pointer; transition: all .2s ease;
    }
    .lp-btn:not(:disabled) {
      background: linear-gradient(135deg, #4299e1, #2b6cb0);
      color: white; box-shadow: 0 4px 20px rgba(66,153,225,.3);
    }
    .lp-btn:not(:disabled):hover { transform: translateY(-1px); box-shadow: 0 6px 28px rgba(66,153,225,.45); }
    .lp-btn:not(:disabled):active { transform: translateY(0); }
    .lp-btn:disabled { background: rgba(255,255,255,.07); color: #4a5568; cursor: not-allowed; }
    .lp-btn-inner { display: flex; align-items: center; justify-content: center; gap: .5rem; }
    .lp-spin {
      width: 15px; height: 15px; border: 2px solid rgba(255,255,255,.25);
      border-top-color: white; border-radius: 50%; animation: lp-spin .6s linear infinite;
    }
    @keyframes lp-spin { to { transform: rotate(360deg); } }
    .lp-badges {
      display: flex; justify-content: center; gap: 1.5rem; margin-top: 2rem;
      padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,.05);
    }
    .lp-badge { display: flex; align-items: center; gap: .3rem; font-size: .68rem; color: #4a5568; }
    @media (max-width: 880px) {
      .lp-root { grid-template-columns: 1fr; }
      .lp-hero { display: none; }
      .lp-panel { padding: 2rem 1.5rem; }
    }
  `;

  return (
    <>
      <style>{styles}</style>
      <div className="lp-root">
        {/* ── Left Hero ── */}
        <div className="lp-hero">
          <div className="lp-brand">
            <div className="lp-brand-icon">🎯</div>
            <span className="lp-brand-name">InterviewAI</span>
          </div>

          <div className="lp-hero-body">
            <p className="lp-eyebrow">AI-Powered Career Platform</p>
            <h1 className="lp-headline">
              Ace every<br />interview with<br /><span className="acc">AI coaching.</span>
            </h1>
            <p className="lp-subtext">
              Practice with adaptive questions tailored to your role. Get instant AI-scored feedback and land the job you deserve.
            </p>
            <div className="lp-stats">
              <div className="lp-stat">
                <div className="lp-stat-n">10K+</div>
                <div className="lp-stat-l">Students</div>
              </div>
              <div className="lp-stat">
                <div className="lp-stat-n">94%</div>
                <div className="lp-stat-l">Offer Rate</div>
              </div>
              <div className="lp-stat">
                <div className="lp-stat-n">50+</div>
                <div className="lp-stat-l">Job Roles</div>
              </div>
            </div>
          </div>

          <div className="lp-testi">
            <p className="lp-testi-q">"I landed my dream job at Google after 3 weeks of practicing. The feedback is incredibly specific and actionable."</p>
            <div className="lp-testi-author">
              <div className="lp-avatar">AS</div>
              <div>
                <div className="lp-author-name">Aisha Sharma</div>
                <div className="lp-author-role">SWE @ Google</div>
              </div>
              <div style={{marginLeft:'auto'}}>
                <div className="lp-stars">★★★★★</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Right Form ── */}
        <div className="lp-panel">
          <div className="lp-box">
            <div className="lp-seg">
              <button className={`lp-seg-btn ${isLogin ? 'on' : ''}`} onClick={() => !isLogin && toggleMode()}>Sign In</button>
              <button className={`lp-seg-btn ${!isLogin ? 'on' : ''}`} onClick={() => isLogin && toggleMode()}>Create Account</button>
            </div>

            <h2 className="lp-title">{isLogin ? 'Welcome back.' : 'Start practicing.'}</h2>
            <p className="lp-sub">{isLogin ? 'Sign in to continue your interview prep.' : 'Create your free account and start today.'}</p>

            {apiError && (
              <div className="lp-err"><span>⚠</span><span>{apiError}</span></div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="lp-fields">
                <div className="lp-field">
                  <label className="lp-label">Username</label>
                  <input className={`lp-input${errors.username ? ' lp-err-inp' : ''}`} name="username" type="text" autoComplete="username" placeholder="e.g. johndoe" value={formData.username} onChange={handleChange} />
                  {errors.username && <span className="lp-ferr">{errors.username}</span>}
                </div>
                {!isLogin && (
                  <div className="lp-field">
                    <label className="lp-label">Email</label>
                    <input className={`lp-input${errors.email ? ' lp-err-inp' : ''}`} name="email" type="email" autoComplete="email" placeholder="you@example.com" value={formData.email} onChange={handleChange} />
                    {errors.email && <span className="lp-ferr">{errors.email}</span>}
                  </div>
                )}
                <div className="lp-field">
                  <label className="lp-label">Password</label>
                  <input className={`lp-input${errors.password ? ' lp-err-inp' : ''}`} name="password" type="password" autoComplete={isLogin ? 'current-password' : 'new-password'} placeholder="Min. 6 characters" value={formData.password} onChange={handleChange} />
                  {errors.password && <span className="lp-ferr">{errors.password}</span>}
                </div>
                {!isLogin && (
                  <div className="lp-field">
                    <label className="lp-label">Confirm Password</label>
                    <input className={`lp-input${errors.confirmPassword ? ' lp-err-inp' : ''}`} name="confirmPassword" type="password" autoComplete="new-password" placeholder="Repeat your password" value={formData.confirmPassword} onChange={handleChange} />
                    {errors.confirmPassword && <span className="lp-ferr">{errors.confirmPassword}</span>}
                  </div>
                )}
              </div>

              <button type="submit" className="lp-btn" disabled={isLoading}>
                <span className="lp-btn-inner">
                  {isLoading && <span className="lp-spin" />}
                  {isLoading ? (isLogin ? 'Signing in...' : 'Creating account...') : (isLogin ? 'Sign In →' : 'Create Account →')}
                </span>
              </button>
            </form>

            <div className="lp-badges">
              <span className="lp-badge">🔒 Secure</span>
              <span className="lp-badge">✦ Free to start</span>
              <span className="lp-badge">⚡ Instant results</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default LoginPage;