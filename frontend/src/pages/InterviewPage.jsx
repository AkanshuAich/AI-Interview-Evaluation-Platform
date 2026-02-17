/**
 * InterviewPage component for answering interview questions.
 *
 * Features:
 * - Fetch and display interview questions
 * - Submit answers to backend
 * - Poll for evaluation status
 * - Display evaluation status (pending/completed/failed)
 * - Loading states and error handling
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { interviewAPI, answerAPI } from '../services/api';

const InterviewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submittedAnswers, setSubmittedAnswers] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState({});

  useEffect(() => { fetchInterview(); }, [id]);

  const fetchInterview = async () => {
    setIsLoading(true); setError('');
    try {
      const response = await interviewAPI.getInterview(id);
      setInterview(response.data);
      const initialAnswers = {};
      response.data.questions.forEach(q => { initialAnswers[q.id] = ''; });
      setAnswers(initialAnswers);
    } catch (error) {
      setError(error.message || 'Failed to load interview');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) =>
    setAnswers(prev => ({ ...prev, [questionId]: value }));

  const handleSubmitAnswer = async (questionId) => {
    const answerText = answers[questionId];
    if (!answerText.trim()) return;
    setSubmitting(prev => ({ ...prev, [questionId]: true }));
    try {
      const response = await answerAPI.submitAnswer(parseInt(id), questionId, answerText);
      setSubmittedAnswers(prev => ({
        ...prev,
        [questionId]: { id: response.data.id, status: 'pending', submitted_at: response.data.submitted_at }
      }));
      pollEvaluationStatus(response.data.id, questionId);
    } catch (error) {
      alert(error.message || 'Failed to submit answer');
    } finally {
      setSubmitting(prev => ({ ...prev, [questionId]: false }));
    }
  };

  const pollEvaluationStatus = async (answerId, questionId) => {
    const maxAttempts = 30;
    let attempts = 0;
    const poll = setInterval(async () => {
      attempts++;
      try {
        const response = await answerAPI.getAnswerStatus(answerId);
        const { evaluation_status } = response.data;
        setSubmittedAnswers(prev => ({
          ...prev,
          [questionId]: { ...prev[questionId], status: evaluation_status }
        }));
        if (evaluation_status !== 'pending' || attempts >= maxAttempts) clearInterval(poll);
      } catch {
        clearInterval(poll);
      }
    }, 1000);
  };

  const allSubmitted = interview && Object.keys(submittedAnswers).length === interview.questions.length;
  const completedCount = Object.values(submittedAnswers).filter(a => a.status === 'completed').length;

  const styles = `
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');
    .iv-root *, .iv-root *::before, .iv-root *::after { box-sizing: border-box; }
    .iv-root { min-height: 100vh; background: #060912; font-family: 'DM Sans', sans-serif; color: #e2e8f0; }

    /* Nav */
    .iv-nav {
      position: sticky; top: 0; z-index: 50;
      display: flex; align-items: center; justify-content: space-between;
      padding: .9rem 2rem; background: rgba(6,9,18,.9); backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255,255,255,.06);
    }
    .iv-nav-left { display: flex; align-items: center; gap: 1rem; }
    .iv-back {
      display: flex; align-items: center; gap: .4rem; background: none; border: none;
      font-family: 'DM Sans', sans-serif; font-size: .8rem; color: #4a5568; cursor: pointer;
      padding: .35rem .5rem; border-radius: 6px; transition: all .2s;
    }
    .iv-back:hover { color: #63b3ed; background: rgba(99,179,237,.07); }
    .iv-nav-sep { width: 1px; height: 20px; background: rgba(255,255,255,.08); }
    .iv-nav-title {
      font-family: 'Syne', sans-serif; font-size: .95rem; font-weight: 700;
      color: #e2e8f0; letter-spacing: -.02em;
    }
    .iv-nav-right { display: flex; align-items: center; gap: .75rem; }
    .iv-progress-text { font-size: .75rem; color: #4a5568; }
    .iv-progress-text span { color: #63b3ed; font-weight: 500; }

    /* Progress bar */
    .iv-prog-bar {
      height: 3px; background: rgba(255,255,255,.05);
      position: relative; overflow: hidden;
    }
    .iv-prog-fill {
      height: 100%; background: linear-gradient(90deg, #4299e1, #63b3ed);
      transition: width .5s ease; border-radius: 0 2px 2px 0;
    }

    /* Main */
    .iv-main { max-width: 780px; margin: 0 auto; padding: 2.5rem 2rem; }

    /* Session info */
    .iv-session-info {
      background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06);
      border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 2rem;
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;
    }
    .iv-session-role {
      font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 800;
      color: #e2e8f0; letter-spacing: -.03em;
    }
    .iv-session-meta { font-size: .8rem; color: #4a5568; margin-top: .25rem; }
    .iv-session-stats { display: flex; gap: 1.5rem; }
    .iv-stat { text-align: center; }
    .iv-stat-n {
      font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800;
      color: #e2e8f0; letter-spacing: -.03em;
    }
    .iv-stat-l { font-size: .65rem; color: #4a5568; text-transform: uppercase; letter-spacing: .07em; }

    /* Question cards */
    .iv-cards { display: flex; flex-direction: column; gap: 1.5rem; }
    .iv-card {
      background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06);
      border-radius: 18px; overflow: hidden; transition: border-color .25s;
    }
    .iv-card.answered { border-color: rgba(104,211,145,.15); }
    .iv-card.evaluating { border-color: rgba(246,173,85,.15); }
    .iv-card-header {
      display: flex; align-items: flex-start; justify-content: space-between;
      padding: 1.5rem 1.5rem 0;
    }
    .iv-q-num {
      font-size: .68rem; font-weight: 500; text-transform: uppercase; letter-spacing: .12em;
      color: #63b3ed; background: rgba(99,179,237,.1); border: 1px solid rgba(99,179,237,.15);
      border-radius: 999px; padding: .25rem .65rem;
    }

    /* Status badges */
    .iv-badge {
      display: inline-flex; align-items: center; gap: .35rem;
      border-radius: 999px; padding: .25rem .75rem; font-size: .72rem; font-weight: 500;
    }
    .iv-badge.pending { background: rgba(246,173,85,.1); border: 1px solid rgba(246,173,85,.2); color: #f6ad55; }
    .iv-badge.completed { background: rgba(104,211,145,.1); border: 1px solid rgba(104,211,145,.2); color: #68d391; }
    .iv-badge.failed { background: rgba(245,101,101,.1); border: 1px solid rgba(245,101,101,.2); color: #fc8181; }
    .iv-badge-dot { width: 6px; height: 6px; border-radius: 50%; }
    .iv-badge.pending .iv-badge-dot { background: #f6ad55; animation: iv-pulse .8s ease-in-out infinite alternate; }
    .iv-badge.completed .iv-badge-dot { background: #68d391; }
    .iv-badge.failed .iv-badge-dot { background: #fc8181; }
    @keyframes iv-pulse { from { opacity: .4; } to { opacity: 1; } }

    .iv-card-body { padding: 1rem 1.5rem 1.5rem; }
    .iv-q-text { font-size: 1rem; color: #cbd5e0; line-height: 1.7; margin-bottom: 1.25rem; font-weight: 300; }

    /* Textarea */
    .iv-textarea {
      width: 100%; padding: 1rem; background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
      font-family: 'DM Sans', sans-serif; font-size: .9rem; color: #e2e8f0;
      outline: none; resize: vertical; transition: border-color .2s, box-shadow .2s, background .2s;
      line-height: 1.65;
    }
    .iv-textarea::placeholder { color: #2d3748; }
    .iv-textarea:focus {
      border-color: rgba(99,179,237,.4); background: rgba(255,255,255,.05);
      box-shadow: 0 0 0 3px rgba(99,179,237,.06);
    }
    .iv-char-hint { font-size: .7rem; color: #2d3748; text-align: right; margin-top: .35rem; }

    .iv-submit {
      margin-top: .875rem; padding: .7rem 1.3rem; border: none; border-radius: 9px;
      font-family: 'Syne', sans-serif; font-size: .875rem; font-weight: 700;
      cursor: pointer; transition: all .2s; display: flex; align-items: center; gap: .4rem;
    }
    .iv-submit:not(:disabled) {
      background: linear-gradient(135deg,#4299e1,#2b6cb0); color: white;
      box-shadow: 0 3px 12px rgba(66,153,225,.3);
    }
    .iv-submit:not(:disabled):hover { transform: translateY(-1px); box-shadow: 0 5px 18px rgba(66,153,225,.4); }
    .iv-submit:disabled { background: rgba(255,255,255,.07); color: #4a5568; cursor: not-allowed; }
    .iv-ispin {
      width: 13px; height: 13px; border: 2px solid rgba(255,255,255,.25);
      border-top-color: white; border-radius: 50%; animation: iv-spin .6s linear infinite;
    }
    @keyframes iv-spin { to { transform: rotate(360deg); } }

    /* Submitted answer display */
    .iv-submitted-wrap { background: rgba(255,255,255,.02); border-radius: 10px; padding: 1rem; }
    .iv-submitted-text {
      font-size: .875rem; color: #a0aec0; line-height: 1.7; white-space: pre-wrap;
      font-weight: 300; margin-bottom: .625rem;
    }
    .iv-submitted-time { font-size: .7rem; color: #2d3748; }

    /* All done banner */
    .iv-done-banner {
      margin-top: 2.5rem; background: linear-gradient(135deg, rgba(104,211,145,.07), rgba(66,153,225,.07));
      border: 1px solid rgba(104,211,145,.15); border-radius: 18px;
      padding: 2rem; text-align: center;
    }
    .iv-done-icon { font-size: 2.5rem; margin-bottom: .75rem; }
    .iv-done-h {
      font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800;
      color: #e2e8f0; letter-spacing: -.04em; margin-bottom: .4rem;
    }
    .iv-done-p { font-size: .85rem; color: #4a5568; margin-bottom: 1.5rem; }
    .iv-report-btn {
      display: inline-flex; align-items: center; gap: .5rem; padding: .875rem 2rem;
      background: linear-gradient(135deg,#48bb78,#38a169); color: white; border: none;
      border-radius: 10px; font-family: 'Syne', sans-serif; font-size: .95rem; font-weight: 700;
      cursor: pointer; transition: all .2s; box-shadow: 0 4px 18px rgba(72,187,120,.3);
    }
    .iv-report-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(72,187,120,.45); }

    /* Loading / error */
    .iv-center { min-height: 100vh; background: #060912; display: flex; align-items: center; justify-content: center; }
    .iv-center-box { text-align: center; }
    .iv-cspinner {
      width: 36px; height: 36px; border: 2.5px solid rgba(255,255,255,.07);
      border-top-color: #63b3ed; border-radius: 50%; animation: iv-spin .7s linear infinite;
      margin: 0 auto 1rem;
    }
    .iv-ctext { font-size: .85rem; color: #4a5568; }
    .iv-cerr { font-size: .9rem; color: #fc8181; margin-bottom: 1rem; }
    .iv-clink { background: none; border: none; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #63b3ed; cursor: pointer; }
    .iv-clink:hover { text-decoration: underline; }

    @media (max-width: 640px) {
      .iv-nav { padding: .75rem 1rem; }
      .iv-main { padding: 1.5rem 1rem; }
      .iv-session-info { flex-direction: column; }
      .iv-card-header, .iv-card-body { padding-left: 1rem; padding-right: 1rem; }
    }
  `;

  if (isLoading) return (
    <>
      <style>{styles}</style>
      <div className="iv-center">
        <div className="iv-center-box">
          <div className="iv-cspinner" />
          <p className="iv-ctext">Loading your interview…</p>
        </div>
      </div>
    </>
  );

  if (error) return (
    <>
      <style>{styles}</style>
      <div className="iv-center">
        <div className="iv-center-box">
          <p className="iv-cerr">⚠ {error}</p>
          <button className="iv-clink" onClick={() => navigate('/dashboard')}>← Back to Dashboard</button>
        </div>
      </div>
    </>
  );

  const submittedCount = Object.keys(submittedAnswers).length;
  const progressPct = interview ? (submittedCount / interview.questions.length) * 100 : 0;

  const getStatusBadge = (status) => {
    const labels = { pending: 'Evaluating…', completed: 'Evaluated', failed: 'Failed' };
    return (
      <span className={`iv-badge ${status}`}>
        <span className="iv-badge-dot" />
        {labels[status] || 'Evaluating…'}
      </span>
    );
  };

  return (
    <>
      <style>{styles}</style>
      <div className="iv-root">
        {/* Nav */}
        <nav className="iv-nav">
          <div className="iv-nav-left">
            <button className="iv-back" onClick={() => navigate('/dashboard')}>← Dashboard</button>
            <div className="iv-nav-sep" />
            <span className="iv-nav-title">{interview.role}</span>
          </div>
          <div className="iv-nav-right">
            <span className="iv-progress-text">
              <span>{submittedCount}</span> / {interview.questions.length} answered
            </span>
          </div>
        </nav>

        {/* Progress bar */}
        <div className="iv-prog-bar">
          <div className="iv-prog-fill" style={{ width: `${progressPct}%` }} />
        </div>

        <main className="iv-main">
          {/* Session info */}
          <div className="iv-session-info">
            <div>
              <div className="iv-session-role">{interview.role}</div>
              <div className="iv-session-meta">Answer all questions at your own pace. Take your time.</div>
            </div>
            <div className="iv-session-stats">
              <div className="iv-stat">
                <div className="iv-stat-n">{interview.questions.length}</div>
                <div className="iv-stat-l">Total</div>
              </div>
              <div className="iv-stat">
                <div className="iv-stat-n">{submittedCount}</div>
                <div className="iv-stat-l">Submitted</div>
              </div>
              <div className="iv-stat">
                <div className="iv-stat-n">{completedCount}</div>
                <div className="iv-stat-l">Scored</div>
              </div>
            </div>
          </div>

          {/* Question cards */}
          <div className="iv-cards">
            {interview.questions.map((question, index) => {
              const submitted = submittedAnswers[question.id];
              const isSubmitting = submitting[question.id];
              const answerText = answers[question.id] || '';

              return (
                <div
                  key={question.id}
                  className={`iv-card ${submitted ? (submitted.status === 'pending' ? 'evaluating' : 'answered') : ''}`}
                >
                  <div className="iv-card-header">
                    <span className="iv-q-num">Question {index + 1} of {interview.questions.length}</span>
                    {submitted && getStatusBadge(submitted.status)}
                  </div>
                  <div className="iv-card-body">
                    <p className="iv-q-text">{question.question_text}</p>

                    {!submitted ? (
                      <>
                        <textarea
                          className="iv-textarea"
                          value={answerText}
                          onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                          rows={6}
                          placeholder="Write your answer here. Be thorough and specific — the AI will evaluate clarity, correctness, and depth."
                        />
                        <p className="iv-char-hint">{answerText.length} characters</p>
                        <button
                          className="iv-submit"
                          onClick={() => handleSubmitAnswer(question.id)}
                          disabled={isSubmitting || !answerText.trim()}
                        >
                          {isSubmitting && <span className="iv-ispin" />}
                          {isSubmitting ? 'Submitting…' : 'Submit Answer →'}
                        </button>
                      </>
                    ) : (
                      <div className="iv-submitted-wrap">
                        <p className="iv-submitted-text">{answerText}</p>
                        <p className="iv-submitted-time">
                          Submitted at {new Date(submitted.submitted_at).toLocaleTimeString()}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* All done */}
          {allSubmitted && (
            <div className="iv-done-banner">
              <div className="iv-done-icon">🎉</div>
              <h3 className="iv-done-h">All answers submitted!</h3>
              <p className="iv-done-p">
                {completedCount < interview.questions.length
                  ? `${completedCount} of ${interview.questions.length} answers evaluated. View the full report when ready.`
                  : 'All answers have been evaluated by AI. View your detailed report now.'}
              </p>
              <button className="iv-report-btn" onClick={() => navigate(`/report/${interview.id}`)}>
                View Complete Report →
              </button>
            </div>
          )}
        </main>
      </div>
    </>
  );
};

export default InterviewPage;