/**
 * DashboardPage component for viewing and creating interviews.
 *
 * Features:
 * - Fetch and display user's interviews
 * - Create new interview with modal form
 * - Navigate to interview page on click
 * - Loading states and error handling
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { interviewAPI } from '../services/api';
import { logout } from '../utils/auth';

const DashboardPage = () => {
  const navigate = useNavigate();
  const [interviews, setInterviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ role: '', num_questions: 5 });
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState('');

  useEffect(() => { fetchInterviews(); }, []);

  const fetchInterviews = async () => {
    setIsLoading(true); setError('');
    try {
      const response = await interviewAPI.listInterviews();
      setInterviews(response.data);
    } catch (error) {
      setError(error.message || 'Failed to load interviews');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateInterview = async (e) => {
    e.preventDefault();
    if (!formData.role.trim()) { setCreateError('Role is required'); return; }
    setIsCreating(true); setCreateError('');
    try {
      const response = await interviewAPI.createInterview(formData.role, formData.num_questions);
      setShowModal(false);
      navigate(`/interview/${response.data.id}`);
    } catch (error) {
      setCreateError(error.message || 'Failed to create interview');
    } finally {
      setIsCreating(false);
    }
  };

  const handleLogout = () => logout();

  const formatDate = (dateString) =>
    new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });

  const roleIcons = {
    default: '💼', python: '🐍', frontend: '⚛️', backend: '⚙️', data: '📊',
    product: '🎯', design: '🎨', devops: '🔧', full: '🖥️', ml: '🤖',
  };
  const getRoleIcon = (role) => {
    const r = role.toLowerCase();
    for (const [key, icon] of Object.entries(roleIcons)) {
      if (r.includes(key)) return icon;
    }
    return roleIcons.default;
  };

  const styles = `
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');
    .db-root *, .db-root *::before, .db-root *::after { box-sizing: border-box; }
    .db-root {
      min-height: 100vh; background: #060912;
      font-family: 'DM Sans', sans-serif; color: #e2e8f0;
    }

    /* Nav */
    .db-nav {
      position: sticky; top: 0; z-index: 50;
      display: flex; align-items: center; justify-content: space-between;
      padding: .9rem 2rem;
      background: rgba(6,9,18,.85); backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255,255,255,.06);
    }
    .db-nav-brand { display: flex; align-items: center; gap: .65rem; }
    .db-nav-icon {
      width: 34px; height: 34px; background: linear-gradient(135deg,#63b3ed,#3182ce);
      border-radius: 9px; display: flex; align-items: center; justify-content: center;
      font-size: 1rem; box-shadow: 0 4px 12px rgba(66,153,225,.3);
    }
    .db-nav-name {
      font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem;
      color: #e2e8f0; letter-spacing: -.02em;
    }
    .db-nav-right { display: flex; align-items: center; gap: 1rem; }
    .db-user-pill {
      display: flex; align-items: center; gap: .5rem;
      background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.07);
      border-radius: 999px; padding: .35rem .75rem; font-size: .78rem; color: #718096;
    }
    .db-user-dot { width: 7px; height: 7px; background: #68d391; border-radius: 50%; }
    .db-logout {
      padding: .4rem .9rem; border: 1px solid rgba(255,255,255,.1); border-radius: 7px;
      background: transparent; font-family: 'DM Sans', sans-serif; font-size: .8rem;
      color: #718096; cursor: pointer; transition: all .2s;
    }
    .db-logout:hover { border-color: rgba(255,255,255,.2); color: #a0aec0; }

    /* Hero strip */
    .db-hero {
      background: linear-gradient(135deg, #0d1528 0%, #060c1a 100%);
      border-bottom: 1px solid rgba(255,255,255,.05);
      padding: 3rem 2rem 2.5rem; position: relative; overflow: hidden;
    }
    .db-hero::before {
      content: ''; position: absolute; top: -100px; right: -100px;
      width: 400px; height: 400px;
      background: radial-gradient(circle, rgba(99,179,237,.1) 0%, transparent 65%);
      border-radius: 50%;
    }
    .db-hero-inner { max-width: 1200px; margin: 0 auto; position: relative; z-index: 1; }
    .db-hero-tag {
      display: inline-flex; align-items: center; gap: .4rem;
      background: rgba(99,179,237,.1); border: 1px solid rgba(99,179,237,.2);
      border-radius: 999px; padding: .3rem .75rem; font-size: .7rem; color: #63b3ed;
      font-weight: 500; letter-spacing: .05em; text-transform: uppercase; margin-bottom: 1rem;
    }
    .db-hero-h {
      font-family: 'Syne', sans-serif; font-size: clamp(1.6rem, 2.5vw, 2.2rem);
      font-weight: 800; letter-spacing: -.04em; color: #f7fafc; margin-bottom: .5rem;
    }
    .db-hero-sub { font-size: .9rem; color: #4a5568; font-weight: 300; max-width: 480px; }
    .db-new-btn {
      display: inline-flex; align-items: center; gap: .5rem;
      background: linear-gradient(135deg,#4299e1,#2b6cb0);
      color: white; border: none; border-radius: 10px; padding: .75rem 1.4rem;
      font-family: 'Syne', sans-serif; font-size: .9rem; font-weight: 700;
      cursor: pointer; transition: all .2s; box-shadow: 0 4px 18px rgba(66,153,225,.3);
      letter-spacing: -.01em; margin-top: 1.5rem;
    }
    .db-new-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(66,153,225,.45); }

    /* Main */
    .db-main { max-width: 1200px; margin: 0 auto; padding: 2.5rem 2rem; }
    .db-section-head {
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;
    }
    .db-section-title {
      font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700;
      color: #e2e8f0; letter-spacing: -.03em;
    }
    .db-count-pill {
      background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08);
      border-radius: 999px; padding: .2rem .6rem; font-size: .72rem; color: #4a5568;
    }

    /* Loading */
    .db-loading { text-align: center; padding: 5rem 0; }
    .db-spinner {
      width: 36px; height: 36px; border: 2.5px solid rgba(255,255,255,.07);
      border-top-color: #63b3ed; border-radius: 50%; animation: db-spin .7s linear infinite;
      margin: 0 auto 1rem;
    }
    @keyframes db-spin { to { transform: rotate(360deg); } }
    .db-loading-text { font-size: .85rem; color: #4a5568; }

    /* Error */
    .db-error {
      background: rgba(245,101,101,.08); border: 1px solid rgba(245,101,101,.2);
      border-radius: 12px; padding: 1rem 1.25rem; font-size: .85rem; color: #fc8181;
    }

    /* Empty state */
    .db-empty {
      text-align: center; padding: 5rem 0;
      background: rgba(255,255,255,.015); border: 1px dashed rgba(255,255,255,.07);
      border-radius: 20px;
    }
    .db-empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: .5; }
    .db-empty-h { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #2d3748; margin-bottom: .5rem; }
    .db-empty-p { font-size: .85rem; color: #2d3748; margin-bottom: 1.5rem; }
    .db-empty-btn {
      display: inline-flex; align-items: center; gap: .4rem;
      background: linear-gradient(135deg,#4299e1,#2b6cb0); color: white;
      border: none; border-radius: 8px; padding: .6rem 1.2rem;
      font-family: 'Syne', sans-serif; font-size: .85rem; font-weight: 700;
      cursor: pointer; box-shadow: 0 4px 14px rgba(66,153,225,.3);
      transition: all .2s;
    }
    .db-empty-btn:hover { transform: translateY(-1px); }

    /* Grid */
    .db-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.25rem; }
    .db-card {
      background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06);
      border-radius: 16px; padding: 1.5rem; cursor: pointer;
      transition: all .25s ease; position: relative; overflow: hidden;
    }
    .db-card::before {
      content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
      background: linear-gradient(90deg, #4299e1, #63b3ed);
      opacity: 0; transition: opacity .25s;
    }
    .db-card:hover {
      background: rgba(255,255,255,.04); border-color: rgba(99,179,237,.25);
      transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,.3);
    }
    .db-card:hover::before { opacity: 1; }
    .db-card-top { display: flex; align-items: flex-start; gap: .875rem; margin-bottom: 1rem; }
    .db-card-icon {
      width: 44px; height: 44px; background: rgba(99,179,237,.1);
      border: 1px solid rgba(99,179,237,.15); border-radius: 11px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; flex-shrink: 0;
    }
    .db-card-role {
      font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700;
      color: #e2e8f0; letter-spacing: -.02em; line-height: 1.2; margin-bottom: .25rem;
    }
    .db-card-meta { font-size: .75rem; color: #4a5568; }
    .db-card-footer {
      display: flex; align-items: center; justify-content: space-between;
      border-top: 1px solid rgba(255,255,255,.05); padding-top: .875rem; margin-top: .5rem;
    }
    .db-card-date { font-size: .72rem; color: #2d3748; }
    .db-card-arrow {
      width: 28px; height: 28px; background: rgba(99,179,237,.1);
      border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font-size: .75rem; color: #63b3ed; transition: transform .2s;
    }
    .db-card:hover .db-card-arrow { transform: translateX(3px); }
    .db-q-badge {
      display: inline-flex; align-items: center; gap: .3rem;
      background: rgba(99,179,237,.08); border: 1px solid rgba(99,179,237,.15);
      border-radius: 999px; padding: .2rem .6rem; font-size: .7rem; color: #63b3ed;
    }

    /* Modal */
    .db-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,.75);
      backdrop-filter: blur(6px); display: flex; align-items: center;
      justify-content: center; padding: 1.5rem; z-index: 100;
      animation: db-fadein .2s ease;
    }
    @keyframes db-fadein { from { opacity: 0; } to { opacity: 1; } }
    .db-modal {
      background: #0d1528; border: 1px solid rgba(255,255,255,.08);
      border-radius: 20px; width: 100%; max-width: 460px; padding: 2rem;
      box-shadow: 0 24px 80px rgba(0,0,0,.6);
      animation: db-slideup .25s ease;
    }
    @keyframes db-slideup { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    .db-modal-h {
      font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800;
      color: #e2e8f0; letter-spacing: -.04em; margin-bottom: .4rem;
    }
    .db-modal-sub { font-size: .82rem; color: #4a5568; margin-bottom: 1.5rem; }
    .db-modal-err {
      background: rgba(245,101,101,.08); border: 1px solid rgba(245,101,101,.25);
      border-radius: 8px; padding: .65rem .9rem; font-size: .8rem; color: #fc8181;
      margin-bottom: 1rem;
    }
    .db-field { margin-bottom: 1.1rem; }
    .db-flabel { font-size: .7rem; font-weight: 500; color: #4a5568; letter-spacing: .07em; text-transform: uppercase; margin-bottom: .4rem; display: block; }
    .db-finput, .db-fselect {
      width: 100%; padding: .75rem 1rem;
      background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
      border-radius: 10px; font-family: 'DM Sans', sans-serif; font-size: .9rem;
      color: #e2e8f0; outline: none; transition: border-color .2s, box-shadow .2s, background .2s;
      -webkit-appearance: none; appearance: none;
    }
    .db-finput::placeholder { color: #2d3748; }
    .db-finput:focus, .db-fselect:focus {
      border-color: rgba(99,179,237,.45); background: rgba(255,255,255,.06);
      box-shadow: 0 0 0 3px rgba(99,179,237,.07);
    }
    .db-fselect { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%234a5568' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 12px center; padding-right: 2rem; }
    .db-fselect option { background: #0d1528; }
    .db-modal-actions { display: flex; gap: .75rem; margin-top: 1.5rem; }
    .db-cancel {
      flex: 1; padding: .75rem; border: 1px solid rgba(255,255,255,.08); border-radius: 10px;
      background: transparent; font-family: 'DM Sans', sans-serif; font-size: .875rem;
      color: #718096; cursor: pointer; transition: all .2s;
    }
    .db-cancel:hover { border-color: rgba(255,255,255,.15); color: #a0aec0; }
    .db-create {
      flex: 2; padding: .75rem; border: none; border-radius: 10px;
      font-family: 'Syne', sans-serif; font-size: .9rem; font-weight: 700;
      cursor: pointer; transition: all .2s; display: flex; align-items: center; justify-content: center; gap: .4rem;
    }
    .db-create:not(:disabled) {
      background: linear-gradient(135deg,#4299e1,#2b6cb0); color: white;
      box-shadow: 0 4px 16px rgba(66,153,225,.3);
    }
    .db-create:not(:disabled):hover { transform: translateY(-1px); box-shadow: 0 6px 22px rgba(66,153,225,.45); }
    .db-create:disabled { background: rgba(255,255,255,.07); color: #4a5568; cursor: not-allowed; }
    .db-cspin {
      width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.25);
      border-top-color: white; border-radius: 50%; animation: db-spin .6s linear infinite;
    }
    @media (max-width: 640px) {
      .db-nav { padding: .75rem 1rem; }
      .db-hero { padding: 2rem 1rem 1.75rem; }
      .db-main { padding: 1.5rem 1rem; }
    }
  `;

  return (
    <>
      <style>{styles}</style>
      <div className="db-root">
        {/* Nav */}
        <nav className="db-nav">
          <div className="db-nav-brand">
            <div className="db-nav-icon">🎯</div>
            <span className="db-nav-name">InterviewAI</span>
          </div>
          <div className="db-nav-right">
            <div className="db-user-pill">
              <span className="db-user-dot" />
              <span>Active</span>
            </div>
            <button className="db-logout" onClick={handleLogout}>Log out</button>
          </div>
        </nav>

        {/* Hero strip */}
        <div className="db-hero">
          <div className="db-hero-inner">
            <span className="db-hero-tag">✦ Your Practice Hub</span>
            <h1 className="db-hero-h">My Interviews</h1>
            <p className="db-hero-sub">Each session is a step closer to your dream role. Keep going.</p>
            <button className="db-new-btn" onClick={() => setShowModal(true)}>
              + New Interview
            </button>
          </div>
        </div>

        {/* Main content */}
        <main className="db-main">
          <div className="db-section-head">
            <span className="db-section-title">All Sessions</span>
            {!isLoading && !error && (
              <span className="db-count-pill">{interviews.length} {interviews.length === 1 ? 'session' : 'sessions'}</span>
            )}
          </div>

          {isLoading && (
            <div className="db-loading">
              <div className="db-spinner" />
              <p className="db-loading-text">Loading your sessions…</p>
            </div>
          )}

          {error && <div className="db-error">⚠ {error}</div>}

          {!isLoading && !error && interviews.length === 0 && (
            <div className="db-empty">
              <div className="db-empty-icon">📋</div>
              <h3 className="db-empty-h">No interviews yet</h3>
              <p className="db-empty-p">Start your first practice session now.</p>
              <button className="db-empty-btn" onClick={() => setShowModal(true)}>+ Create Interview</button>
            </div>
          )}

          {!isLoading && !error && interviews.length > 0 && (
            <div className="db-grid">
              {interviews.map((interview) => (
                <div key={interview.id} className="db-card" onClick={() => navigate(`/interview/${interview.id}`)}>
                  <div className="db-card-top">
                    <div className="db-card-icon">{getRoleIcon(interview.role)}</div>
                    <div>
                      <div className="db-card-role">{interview.role}</div>
                      <span className="db-q-badge">❓ {interview.questions.length} questions</span>
                    </div>
                  </div>
                  <div className="db-card-footer">
                    <span className="db-card-date">📅 {formatDate(interview.created_at)}</span>
                    <div className="db-card-arrow">→</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>

        {/* Modal */}
        {showModal && (
          <div className="db-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
            <div className="db-modal">
              <h3 className="db-modal-h">New Interview</h3>
              <p className="db-modal-sub">Configure your practice session.</p>

              {createError && <div className="db-modal-err">⚠ {createError}</div>}

              <form onSubmit={handleCreateInterview}>
                <div className="db-field">
                  <label className="db-flabel">Job Role</label>
                  <input
                    className="db-finput"
                    type="text"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    placeholder="e.g. Senior Python Developer"
                  />
                </div>
                <div className="db-field">
                  <label className="db-flabel">Number of Questions</label>
                  <select
                    className="db-fselect"
                    value={formData.num_questions}
                    onChange={(e) => setFormData({ ...formData, num_questions: parseInt(e.target.value) })}
                  >
                    <option value={3}>3 questions — Quick practice</option>
                    <option value={5}>5 questions — Standard session</option>
                    <option value={10}>10 questions — Full mock interview</option>
                  </select>
                </div>
                <div className="db-modal-actions">
                  <button type="button" className="db-cancel" onClick={() => setShowModal(false)} disabled={isCreating}>Cancel</button>
                  <button type="submit" className="db-create" disabled={isCreating}>
                    {isCreating && <span className="db-cspin" />}
                    {isCreating ? 'Creating…' : 'Start Interview →'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default DashboardPage;