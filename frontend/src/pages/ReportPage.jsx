/**
 * ReportPage component for viewing complete interview reports with evaluations.
 *
 * Features:
 * - Fetch and display complete interview report
 * - Display all questions with answers and evaluations
 * - Visual score representation with progress bars
 * - Display feedback and suggestions
 * - Calculate and display overall interview score
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { reportAPI } from '../services/api';

const ScoreBar = ({ label, score, icon }) => {
  const pct = (score / 10) * 100;
  const color = score >= 8 ? '#68d391' : score >= 6 ? '#f6ad55' : '#fc8181';
  const bgColor = score >= 8 ? 'rgba(104,211,145,.12)' : score >= 6 ? 'rgba(246,173,85,.12)' : 'rgba(245,101,101,.12)';

  return (
    <div style={{
      background: bgColor, borderRadius: 10, padding: '.75rem 1rem', marginBottom: '.625rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '.45rem' }}>
        <span style={{ fontSize: '.78rem', color: '#a0aec0', fontWeight: 400 }}>{icon} {label}</span>
        <span style={{ fontFamily: "'Syne', sans-serif", fontSize: '.95rem', fontWeight: 800, color, letterSpacing: '-.02em' }}>
          {score.toFixed(1)}<span style={{ fontSize: '.65rem', color: '#4a5568', fontWeight: 400 }}>/10</span>
        </span>
      </div>
      <div style={{ background: 'rgba(255,255,255,.07)', borderRadius: 999, height: 4, overflow: 'hidden' }}>
        <div style={{
          width: `${pct}%`, height: '100%', background: color,
          borderRadius: 999, transition: 'width .8s ease'
        }} />
      </div>
    </div>
  );
};

const ReportPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedQ, setExpandedQ] = useState({});

  useEffect(() => { fetchReport(); }, [id]);

  const fetchReport = async () => {
    setIsLoading(true); setError('');
    try {
      const response = await reportAPI.getInterviewReport(id);
      setReport(response.data);
      // Expand first question by default
      if (response.data.questions.length > 0) {
        setExpandedQ({ [response.data.questions[0].question_id]: true });
      }
    } catch (error) {
      setError(error.message || 'Failed to load report');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleExpanded = (qId) =>
    setExpandedQ(prev => ({ ...prev, [qId]: !prev[qId] }));

  const getScoreLabel = (score) => {
    if (score >= 9) return { label: 'Excellent', color: '#68d391' };
    if (score >= 8) return { label: 'Great', color: '#68d391' };
    if (score >= 7) return { label: 'Good', color: '#f6ad55' };
    if (score >= 6) return { label: 'Fair', color: '#f6ad55' };
    return { label: 'Needs Work', color: '#fc8181' };
  };

  const styles = `
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');
    .rp-root *, .rp-root *::before, .rp-root *::after { box-sizing: border-box; }
    .rp-root { min-height: 100vh; background: #060912; font-family: 'DM Sans', sans-serif; color: #e2e8f0; }

    /* Nav */
    .rp-nav {
      position: sticky; top: 0; z-index: 50;
      display: flex; align-items: center; justify-content: space-between;
      padding: .9rem 2rem; background: rgba(6,9,18,.9); backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255,255,255,.06);
    }
    .rp-nav-left { display: flex; align-items: center; gap: 1rem; }
    .rp-back {
      display: flex; align-items: center; gap: .4rem; background: none; border: none;
      font-family: 'DM Sans', sans-serif; font-size: .8rem; color: #4a5568; cursor: pointer;
      padding: .35rem .5rem; border-radius: 6px; transition: all .2s;
    }
    .rp-back:hover { color: #63b3ed; background: rgba(99,179,237,.07); }
    .rp-nav-sep { width: 1px; height: 20px; background: rgba(255,255,255,.08); }
    .rp-nav-title {
      font-family: 'Syne', sans-serif; font-size: .95rem; font-weight: 700;
      color: #e2e8f0; letter-spacing: -.02em;
    }

    /* Hero / score card */
    .rp-hero {
      background: linear-gradient(145deg, #0d1528 0%, #060c1a 100%);
      border-bottom: 1px solid rgba(255,255,255,.05); position: relative; overflow: hidden;
    }
    .rp-hero::before {
      content: ''; position: absolute; top: -120px; right: -120px;
      width: 450px; height: 450px;
      background: radial-gradient(circle, rgba(99,179,237,.1) 0%, transparent 65%);
      border-radius: 50%;
    }
    .rp-hero-inner { max-width: 860px; margin: 0 auto; padding: 2.5rem 2rem; position: relative; z-index: 1; }
    .rp-hero-tag {
      display: inline-flex; align-items: center; gap: .4rem;
      background: rgba(99,179,237,.1); border: 1px solid rgba(99,179,237,.2);
      border-radius: 999px; padding: .25rem .75rem; font-size: .68rem; color: #63b3ed;
      font-weight: 500; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 1rem;
    }
    .rp-hero-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 2rem; flex-wrap: wrap; }
    .rp-hero-left {}
    .rp-hero-role {
      font-family: 'Syne', sans-serif; font-size: clamp(1.5rem, 2.5vw, 2rem);
      font-weight: 800; color: #f7fafc; letter-spacing: -.045em; margin-bottom: .5rem;
    }
    .rp-hero-meta { font-size: .82rem; color: #4a5568; display: flex; gap: 1rem; flex-wrap: wrap; }
    .rp-hero-meta-item { display: flex; align-items: center; gap: .3rem; }

    /* Score donut-style widget */
    .rp-score-widget {
      background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.07);
      border-radius: 18px; padding: 1.5rem 2rem; text-align: center; flex-shrink: 0;
      min-width: 160px;
    }
    .rp-score-label { font-size: .65rem; color: #4a5568; text-transform: uppercase; letter-spacing: .12em; margin-bottom: .625rem; }
    .rp-score-num {
      font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800;
      letter-spacing: -.06em; line-height: 1;
    }
    .rp-score-denom { font-size: .85rem; color: #4a5568; font-weight: 300; }
    .rp-score-grade {
      display: inline-block; margin-top: .5rem; font-size: .72rem; font-weight: 600;
      padding: .2rem .6rem; border-radius: 999px;
    }

    /* Q stats bar */
    .rp-stats-bar {
      display: grid; grid-template-columns: repeat(3,1fr); gap: .75rem;
      margin-top: 1.75rem;
    }
    .rp-stat {
      background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06);
      border-radius: 12px; padding: .875rem; text-align: center;
    }
    .rp-stat-n {
      font-family: 'Syne', sans-serif; font-size: 1.35rem; font-weight: 800;
      color: #e2e8f0; letter-spacing: -.03em;
    }
    .rp-stat-l { font-size: .65rem; color: #4a5568; margin-top: .2rem; text-transform: uppercase; letter-spacing: .07em; }

    /* Main */
    .rp-main { max-width: 860px; margin: 0 auto; padding: 2.5rem 2rem; }
    .rp-section-h {
      font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700;
      color: #e2e8f0; letter-spacing: -.03em; margin-bottom: 1.25rem;
    }

    /* Q cards */
    .rp-qcard {
      background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06);
      border-radius: 18px; margin-bottom: 1.25rem; overflow: hidden; transition: border-color .2s;
    }
    .rp-qcard.has-eval { border-color: rgba(99,179,237,.1); }
    .rp-qcard-head {
      display: flex; align-items: center; justify-content: space-between;
      padding: 1.25rem 1.5rem; cursor: pointer; gap: 1rem;
    }
    .rp-qcard-head:hover { background: rgba(255,255,255,.015); }
    .rp-qcard-head-left { display: flex; align-items: center; gap: .875rem; flex: 1; min-width: 0; }
    .rp-qnum {
      font-size: .65rem; font-weight: 500; text-transform: uppercase; letter-spacing: .12em;
      color: #63b3ed; background: rgba(99,179,237,.1); border: 1px solid rgba(99,179,237,.15);
      border-radius: 999px; padding: .22rem .65rem; flex-shrink: 0;
    }
    .rp-qpreview {
      font-size: .875rem; color: #718096; font-weight: 300; white-space: nowrap;
      overflow: hidden; text-overflow: ellipsis;
    }
    .rp-qcard-head-right { display: flex; align-items: center; gap: .75rem; flex-shrink: 0; }
    .rp-mini-score {
      font-family: 'Syne', sans-serif; font-size: .85rem; font-weight: 800;
      letter-spacing: -.02em;
    }
    .rp-chevron { font-size: .7rem; color: #4a5568; transition: transform .25s; }
    .rp-chevron.open { transform: rotate(180deg); }
    .rp-qcard-body { border-top: 1px solid rgba(255,255,255,.05); }

    /* Q text */
    .rp-q-text {
      font-size: 1rem; color: #cbd5e0; line-height: 1.7; font-weight: 300;
      padding: 1.25rem 1.5rem 0;
    }

    /* Answer box */
    .rp-answer-box { padding: 1rem 1.5rem; }
    .rp-answer-label { font-size: .65rem; text-transform: uppercase; letter-spacing: .12em; color: #4a5568; margin-bottom: .5rem; }
    .rp-answer-text {
      background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.05);
      border-radius: 10px; padding: .875rem 1rem;
      font-size: .875rem; color: #a0aec0; line-height: 1.7; white-space: pre-wrap; font-weight: 300;
    }

    /* Eval section */
    .rp-eval { padding: 1.25rem 1.5rem; border-top: 1px solid rgba(255,255,255,.05); }
    .rp-eval-h { font-size: .65rem; text-transform: uppercase; letter-spacing: .12em; color: #4a5568; margin-bottom: 1rem; }

    .rp-feedback-box {
      background: rgba(99,179,237,.06); border: 1px solid rgba(99,179,237,.12);
      border-radius: 10px; padding: .875rem 1rem; font-size: .875rem; color: #a0aec0;
      line-height: 1.7; margin-bottom: 1rem; font-weight: 300;
    }
    .rp-feedback-tag { font-size: .65rem; color: #63b3ed; text-transform: uppercase; letter-spacing: .1em; margin-bottom: .4rem; font-weight: 500; }

    .rp-suggestions { margin-top: 1rem; }
    .rp-sug-title { font-size: .65rem; text-transform: uppercase; letter-spacing: .12em; color: #4a5568; margin-bottom: .625rem; }
    .rp-sug-item {
      display: flex; align-items: flex-start; gap: .625rem;
      padding: .625rem .875rem; background: rgba(246,173,85,.05);
      border: 1px solid rgba(246,173,85,.1); border-radius: 8px; margin-bottom: .4rem;
    }
    .rp-sug-icon { color: #f6ad55; font-size: .75rem; margin-top: .1rem; flex-shrink: 0; }
    .rp-sug-text { font-size: .825rem; color: #a0aec0; line-height: 1.6; font-weight: 300; }

    .rp-status-pending { padding: .875rem; text-align: center; }
    .rp-status-pending-text { font-size: .8rem; color: #f6ad55; display: flex; align-items: center; justify-content: center; gap: .4rem; }
    .rp-pulsedot { width: 7px; height: 7px; background: #f6ad55; border-radius: 50%; animation: rp-pulse .8s ease-in-out infinite alternate; }
    @keyframes rp-pulse { from { opacity: .3; } to { opacity: 1; } }

    .rp-status-failed { padding: .875rem; font-size: .8rem; color: #fc8181; text-align: center; }

    /* No answer */
    .rp-no-answer { padding: 1.25rem 1.5rem; font-size: .85rem; color: #2d3748; font-style: italic; }

    /* Loading / error */
    .rp-center { min-height: 100vh; background: #060912; display: flex; align-items: center; justify-content: center; }
    .rp-center-box { text-align: center; }
    .rp-cspinner {
      width: 36px; height: 36px; border: 2.5px solid rgba(255,255,255,.07);
      border-top-color: #63b3ed; border-radius: 50%; animation: rp-spin .7s linear infinite; margin: 0 auto 1rem;
    }
    @keyframes rp-spin { to { transform: rotate(360deg); } }
    .rp-ctext { font-size: .85rem; color: #4a5568; }
    .rp-cerr { font-size: .9rem; color: #fc8181; margin-bottom: 1rem; }
    .rp-clink { background: none; border: none; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #63b3ed; cursor: pointer; }
    .rp-clink:hover { text-decoration: underline; }

    @media (max-width: 640px) {
      .rp-nav { padding: .75rem 1rem; }
      .rp-hero-inner, .rp-main { padding-left: 1rem; padding-right: 1rem; }
      .rp-hero-row { flex-direction: column; }
      .rp-score-widget { align-self: flex-start; }
      .rp-qcard-head { padding: 1rem; }
      .rp-q-text, .rp-answer-box, .rp-eval { padding-left: 1rem; padding-right: 1rem; }
    }
  `;

  if (isLoading) return (
    <>
      <style>{styles}</style>
      <div className="rp-center">
        <div className="rp-center-box">
          <div className="rp-cspinner" />
          <p className="rp-ctext">Loading your report…</p>
        </div>
      </div>
    </>
  );

  if (error) return (
    <>
      <style>{styles}</style>
      <div className="rp-center">
        <div className="rp-center-box">
          <p className="rp-cerr">⚠ {error}</p>
          <button className="rp-clink" onClick={() => navigate('/dashboard')}>← Back to Dashboard</button>
        </div>
      </div>
    </>
  );

  const answeredCount = report.questions.filter(q => q.answer).length;
  const evaluatedCount = report.questions.filter(q => q.answer?.evaluation?.status === 'completed').length;
  const scoreLabel = report.overall_score !== null ? getScoreLabel(report.overall_score) : null;

  return (
    <>
      <style>{styles}</style>
      <div className="rp-root">
        {/* Nav */}
        <nav className="rp-nav">
          <div className="rp-nav-left">
            <button className="rp-back" onClick={() => navigate('/dashboard')}>← Dashboard</button>
            <div className="rp-nav-sep" />
            <span className="rp-nav-title">Interview Report</span>
          </div>
        </nav>

        {/* Hero */}
        <div className="rp-hero">
          <div className="rp-hero-inner">
            <span className="rp-hero-tag">✦ Performance Report</span>
            <div className="rp-hero-row">
              <div className="rp-hero-left">
                <h1 className="rp-hero-role">{report.role}</h1>
                <div className="rp-hero-meta">
                  <span className="rp-hero-meta-item">📅 {new Date(report.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                  <span className="rp-hero-meta-item">❓ {report.questions.length} questions</span>
                </div>
                <div className="rp-stats-bar">
                  <div className="rp-stat">
                    <div className="rp-stat-n">{answeredCount}</div>
                    <div className="rp-stat-l">Answered</div>
                  </div>
                  <div className="rp-stat">
                    <div className="rp-stat-n">{evaluatedCount}</div>
                    <div className="rp-stat-l">Evaluated</div>
                  </div>
                  <div className="rp-stat">
                    <div className="rp-stat-n">{report.questions.length - answeredCount}</div>
                    <div className="rp-stat-l">Skipped</div>
                  </div>
                </div>
              </div>
              {report.overall_score !== null && scoreLabel && (
                <div className="rp-score-widget">
                  <div className="rp-score-label">Overall Score</div>
                  <div className="rp-score-num" style={{ color: scoreLabel.color }}>
                    {report.overall_score.toFixed(1)}
                  </div>
                  <div className="rp-score-denom">out of 10</div>
                  <span
                    className="rp-score-grade"
                    style={{ background: `${scoreLabel.color}18`, color: scoreLabel.color }}
                  >
                    {scoreLabel.label}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Question list */}
        <main className="rp-main">
          <h2 className="rp-section-h">Question Breakdown</h2>
          {report.questions.map((question, index) => {
            const hasEval = question.answer?.evaluation?.status === 'completed';
            const avgScore = hasEval
              ? (Object.values(question.answer.evaluation.scores).reduce((a, b) => a + b, 0) / Object.values(question.answer.evaluation.scores).length)
              : null;
            const isOpen = expandedQ[question.question_id];

            return (
              <div
                key={question.question_id}
                className={`rp-qcard ${hasEval ? 'has-eval' : ''}`}
              >
                {/* Collapsible header */}
                <div className="rp-qcard-head" onClick={() => toggleExpanded(question.question_id)}>
                  <div className="rp-qcard-head-left">
                    <span className="rp-qnum">Q{index + 1}</span>
                    <span className="rp-qpreview">{question.question_text}</span>
                  </div>
                  <div className="rp-qcard-head-right">
                    {avgScore !== null && (
                      <span className="rp-mini-score" style={{ color: getScoreLabel(avgScore).color }}>
                        {avgScore.toFixed(1)}
                      </span>
                    )}
                    <span className={`rp-chevron ${isOpen ? 'open' : ''}`}>▼</span>
                  </div>
                </div>

                {/* Expanded body */}
                {isOpen && (
                  <div className="rp-qcard-body">
                    <p className="rp-q-text">{question.question_text}</p>

                    {question.answer ? (
                      <>
                        {/* Answer */}
                        <div className="rp-answer-box">
                          <div className="rp-answer-label">Your Answer</div>
                          <div className="rp-answer-text">{question.answer.answer_text}</div>
                        </div>

                        {/* Evaluation */}
                        {hasEval ? (
                          <div className="rp-eval">
                            <div className="rp-eval-h">AI Evaluation</div>

                            {/* Score bars */}
                            <ScoreBar label="Correctness" score={question.answer.evaluation.scores.correctness} icon="✓" />
                            <ScoreBar label="Completeness" score={question.answer.evaluation.scores.completeness} icon="⬚" />
                            <ScoreBar label="Quality" score={question.answer.evaluation.scores.quality} icon="◈" />
                            <ScoreBar label="Communication" score={question.answer.evaluation.scores.communication} icon="◎" />

                            {/* Feedback */}
                            {question.answer.evaluation.feedback && (
                              <div className="rp-feedback-box">
                                <div className="rp-feedback-tag">AI Feedback</div>
                                {question.answer.evaluation.feedback}
                              </div>
                            )}

                            {/* Suggestions */}
                            {question.answer.evaluation.suggestions?.length > 0 && (
                              <div className="rp-suggestions">
                                <div className="rp-sug-title">Suggestions for Improvement</div>
                                {question.answer.evaluation.suggestions.map((s, i) => (
                                  <div key={i} className="rp-sug-item">
                                    <span className="rp-sug-icon">→</span>
                                    <span className="rp-sug-text">{s}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ) : question.answer.evaluation?.status === 'pending' ? (
                          <div className="rp-eval rp-status-pending">
                            <div className="rp-status-pending-text">
                              <span className="rp-pulsedot" /> Evaluation in progress…
                            </div>
                          </div>
                        ) : question.answer.evaluation?.status === 'failed' ? (
                          <div className="rp-eval rp-status-failed">⚠ Evaluation failed for this question</div>
                        ) : null}
                      </>
                    ) : (
                      <div className="rp-no-answer">No answer was submitted for this question.</div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </main>
      </div>
    </>
  );
};

export default ReportPage;