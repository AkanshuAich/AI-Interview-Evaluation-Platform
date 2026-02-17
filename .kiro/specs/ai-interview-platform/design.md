# Design Document: AI Interview Evaluation Platform

## Overview

The AI Interview Evaluation Platform is a full-stack application built with Python FastAPI backend and React frontend. The system enables automated technical interview evaluation through LLM-powered assessment, providing structured feedback and scoring for candidate responses.

The architecture follows a clean separation of concerns with modular backend design (routers, services, models, schemas) and a professional React dashboard frontend. The backend uses async patterns throughout for optimal performance, with background task processing for LLM evaluations to maintain API responsiveness.

Key design principles:
- **Simplicity**: Monolithic architecture avoiding microservices complexity
- **Modularity**: Clear separation between routing, business logic, and data layers
- **Async-first**: Non-blocking I/O for all database and external service calls
- **Scalability**: Background task processing and connection pooling for growth
- **Deployability**: Environment-based configuration for easy cloud deployment

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (React + Vite)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Login   │  │Dashboard │  │Interview │  │  Report  │   │
│  │   Page   │  │   Page   │  │   Page   │  │   Page   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                          │                                   │
│                    API Client Layer                          │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTPS/JSON
                           │ JWT Auth
┌──────────────────────────┼──────────────────────────────────┐
│                          ▼                                   │
│                   FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │                  API Routers                        │    │
│  │  /auth  /interviews  /answers  /reports            │    │
│  └─────────────┬──────────────────────────────────────┘    │
│                │                                             │
│  ┌─────────────▼──────────────────────────────────────┐    │
│  │              Service Layer                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │    │
│  │  │   Auth   │  │Interview │  │   LLM Service    │ │    │
│  │  │ Service  │  │ Service  │  │  (OpenAI/etc)    │ │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘ │    │
│  │  ┌──────────┐  ┌──────────────────────────────┐   │    │
│  │  │ Answer   │  │  Background Task Queue       │   │    │
│  │  │ Service  │  │  (Evaluation Pipeline)       │   │    │
│  │  └──────────┘  └──────────────────────────────┘   │    │
│  └─────────────┬──────────────────────────────────────┘    │
│                │                                             │
│  ┌─────────────▼──────────────────────────────────────┐    │
│  │          SQLAlchemy ORM Layer                       │    │
│  │  Models: User, Interview, Question, Answer,        │    │
│  │          Evaluation                                 │    │
│  └─────────────┬──────────────────────────────────────┘    │
└────────────────┼─────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────┐
│                    PostgreSQL Database                        │
│  Tables: users, interviews, questions, answers, evaluations  │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- SQLAlchemy 2.0 (async ORM)
- PostgreSQL (database)
- Pydantic (data validation)
- python-jose (JWT tokens)
- passlib (password hashing)
- httpx (async HTTP client for LLM APIs)
- python-multipart (file uploads)

**Frontend:**
- React 18
- Vite (build tool)
- React Router (navigation)
- Axios (HTTP client)
- TailwindCSS or Material-UI (styling)

**Background Tasks:**
- FastAPI BackgroundTasks (simple async task execution)
- Alternative: Celery + Redis (for production scale)

## Components and Interfaces

### Backend Components

#### 1. API Routers (`app/routers/`)

**auth_router.py**
```python
POST /api/auth/register
  Request: { username: str, email: str, password: str }
  Response: { user_id: int, message: str }

POST /api/auth/login
  Request: { username: str, password: str }
  Response: { access_token: str, token_type: str }

GET /api/auth/me
  Headers: Authorization: Bearer <token>
  Response: { user_id: int, username: str, email: str }
```

**interview_router.py**
```python
POST /api/interviews
  Headers: Authorization: Bearer <token>
  Request: { role: str, num_questions: int }
  Response: { interview_id: int, role: str, questions: [Question] }

GET /api/interviews
  Headers: Authorization: Bearer <token>
  Response: { interviews: [Interview] }

GET /api/interviews/{interview_id}
  Headers: Authorization: Bearer <token>
  Response: { interview_id: int, role: str, questions: [Question], created_at: datetime }
```

**answer_router.py**
```python
POST /api/answers
  Headers: Authorization: Bearer <token>
  Request: { interview_id: int, question_id: int, answer_text: str }
  Response: { answer_id: int, status: "submitted", message: str }

GET /api/answers/{answer_id}/status
  Headers: Authorization: Bearer <token>
  Response: { answer_id: int, evaluation_status: str, evaluation: Evaluation? }
```

**report_router.py**
```python
GET /api/reports/{interview_id}
  Headers: Authorization: Bearer <token>
  Response: {
    interview_id: int,
    role: str,
    questions: [{
      question_id: int,
      question_text: str,
      answer: {
        answer_text: str,
        evaluation: {
          scores: { correctness: float, completeness: float, quality: float },
          feedback: str,
          suggestions: [str]
        }
      }?
    }],
    overall_score: float?
  }
```

#### 2. Service Layer (`app/services/`)

**auth_service.py**
- `hash_password(password: str) -> str`: Hash password using bcrypt
- `verify_password(plain: str, hashed: str) -> bool`: Verify password
- `create_access_token(data: dict) -> str`: Generate JWT token
- `verify_token(token: str) -> dict`: Decode and validate JWT
- `get_current_user(token: str) -> User`: Extract user from token

**interview_service.py**
- `create_interview(user_id: int, role: str, num_questions: int) -> Interview`: Create interview with LLM-generated questions
- `get_user_interviews(user_id: int) -> List[Interview]`: Fetch user's interviews
- `get_interview_by_id(interview_id: int) -> Interview`: Fetch specific interview

**answer_service.py**
- `submit_answer(interview_id: int, question_id: int, answer_text: str, user_id: int) -> Answer`: Save answer and trigger evaluation
- `get_answer_with_evaluation(answer_id: int) -> Answer`: Fetch answer with evaluation results

**llm_service.py**
- `generate_questions(role: str, num_questions: int) -> List[str]`: Generate interview questions using LLM
- `evaluate_answer(question: str, answer: str, role: str) -> EvaluationResult`: Evaluate answer using LLM
- `_build_question_prompt(role: str, num_questions: int) -> str`: Build prompt for question generation
- `_build_evaluation_prompt(question: str, answer: str, role: str) -> str`: Build prompt for evaluation
- `_call_llm_api(prompt: str) -> str`: Make async API call to LLM provider

**evaluation_service.py**
- `evaluate_answer_async(answer_id: int)`: Background task to evaluate answer
- `parse_evaluation_response(llm_response: str) -> EvaluationResult`: Parse LLM response into structured format
- `save_evaluation(answer_id: int, evaluation: EvaluationResult)`: Persist evaluation to database

#### 3. Database Models (`app/models/`)

**user.py**
```python
class User(Base):
    id: int (PK)
    username: str (unique, indexed)
    email: str (unique, indexed)
    hashed_password: str
    created_at: datetime
    interviews: relationship -> Interview
```

**interview.py**
```python
class Interview(Base):
    id: int (PK)
    user_id: int (FK -> User)
    role: str
    created_at: datetime
    user: relationship -> User
    questions: relationship -> Question
```

**question.py**
```python
class Question(Base):
    id: int (PK)
    interview_id: int (FK -> Interview)
    question_text: str
    question_order: int
    interview: relationship -> Interview
    answers: relationship -> Answer
```

**answer.py**
```python
class Answer(Base):
    id: int (PK)
    question_id: int (FK -> Question)
    user_id: int (FK -> User)
    answer_text: str
    submitted_at: datetime
    question: relationship -> Question
    user: relationship -> User
    evaluation: relationship -> Evaluation (one-to-one)
```

**evaluation.py**
```python
class Evaluation(Base):
    id: int (PK)
    answer_id: int (FK -> Answer, unique)
    scores: JSON  # { correctness: float, completeness: float, quality: float, communication: float }
    feedback: str
    suggestions: JSON  # [str]
    evaluated_at: datetime
    status: str  # "pending", "completed", "failed"
    answer: relationship -> Answer
```

#### 4. Pydantic Schemas (`app/schemas/`)

**auth_schemas.py**
```python
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str (min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
```

**interview_schemas.py**
```python
class InterviewCreate(BaseModel):
    role: str
    num_questions: int (ge=1, le=10)

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_order: int

class InterviewResponse(BaseModel):
    id: int
    role: str
    created_at: datetime
    questions: List[QuestionResponse]
```

**answer_schemas.py**
```python
class AnswerSubmit(BaseModel):
    interview_id: int
    question_id: int
    answer_text: str (min_length=10)

class EvaluationScores(BaseModel):
    correctness: float (ge=0, le=10)
    completeness: float (ge=0, le=10)
    quality: float (ge=0, le=10)
    communication: float (ge=0, le=10)

class EvaluationResponse(BaseModel):
    scores: EvaluationScores
    feedback: str
    suggestions: List[str]
    evaluated_at: datetime
    status: str

class AnswerResponse(BaseModel):
    id: int
    answer_text: str
    submitted_at: datetime
    evaluation: Optional[EvaluationResponse]
```

**report_schemas.py**
```python
class QuestionWithAnswer(BaseModel):
    question_id: int
    question_text: str
    answer: Optional[AnswerResponse]

class InterviewReport(BaseModel):
    interview_id: int
    role: str
    created_at: datetime
    questions: List[QuestionWithAnswer]
    overall_score: Optional[float]
```

### Frontend Components

#### Page Components

**LoginPage.jsx**
- Login form with username/password
- Calls `/api/auth/login`
- Stores JWT token in localStorage
- Redirects to Dashboard on success

**DashboardPage.jsx**
- Displays list of user's interviews
- "Create New Interview" button
- Shows interview role, date, and status
- Click interview to view report

**InterviewPage.jsx**
- Displays questions one at a time or all at once
- Text area for answer submission
- Submit button triggers `/api/answers`
- Shows submission confirmation
- Displays evaluation status (pending/completed)

**ReportPage.jsx**
- Fetches `/api/reports/{interview_id}`
- Displays all questions with answers
- Shows evaluation scores with visual indicators (progress bars, color coding)
- Displays feedback and suggestions
- Shows overall interview score

#### Utility Components

**ProtectedRoute.jsx**
- Wraps authenticated routes
- Checks for valid JWT token
- Redirects to login if unauthenticated

**ApiClient.js**
- Axios instance with base URL configuration
- Automatic JWT token injection in headers
- Error handling and token refresh logic

**ScoreDisplay.jsx**
- Reusable component for displaying scores
- Visual representation (progress bar, gauge)
- Color coding (red/yellow/green based on score)

## Data Models

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Interviews table
CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_order INTEGER NOT NULL,
    INDEX idx_interview_id (interview_id)
);

-- Answers table
CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_question_id (question_id),
    INDEX idx_user_id (user_id)
);

-- Evaluations table
CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    answer_id INTEGER UNIQUE NOT NULL REFERENCES answers(id) ON DELETE CASCADE,
    scores JSONB NOT NULL,
    feedback TEXT NOT NULL,
    suggestions JSONB NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    INDEX idx_answer_id (answer_id),
    INDEX idx_status (status)
);
```

### Data Flow

**Interview Creation Flow:**
1. User submits role via Frontend
2. Backend receives request, validates JWT
3. `interview_service.create_interview()` calls `llm_service.generate_questions()`
4. LLM service makes async API call to LLM provider
5. Questions are parsed and saved to database
6. Interview with questions returned to Frontend

**Answer Submission and Evaluation Flow:**
1. User submits answer via Frontend
2. Backend receives request, validates JWT and interview ownership
3. `answer_service.submit_answer()` saves answer to database
4. Background task `evaluation_service.evaluate_answer_async()` is triggered
5. Backend immediately returns success response (non-blocking)
6. Background task calls `llm_service.evaluate_answer()`
7. LLM response is parsed into structured evaluation
8. Evaluation saved to database with status "completed"
9. Frontend polls `/api/answers/{answer_id}/status` or uses WebSocket for real-time updates

**Report Retrieval Flow:**
1. User requests report via Frontend
2. Backend validates JWT and interview access
3. Database query joins interviews, questions, answers, and evaluations
4. Structured report with all data returned to Frontend
5. Frontend renders questions, answers, scores, and feedback

### Configuration Management

**Backend Environment Variables:**
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
SECRET_KEY=<jwt-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LLM_API_KEY=<openai-or-other-llm-api-key>
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

**Frontend Environment Variables:**
```
VITE_API_BASE_URL=http://localhost:8000/api
```

## Correctness Properties


A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Authentication and Security Properties

**Property 1: Valid credentials produce valid JWT tokens**
*For any* valid user credentials (username and password), when authentication is requested, the Auth_Service should return a valid JWT token that can be decoded and verified.
**Validates: Requirements 1.1**

**Property 2: Invalid credentials are rejected**
*For any* invalid credentials (wrong password, non-existent user, malformed input), when authentication is attempted, the Auth_Service should return an authentication error and not generate a token.
**Validates: Requirements 1.2**

**Property 3: JWT token validation on protected endpoints**
*For any* authenticated API endpoint, when a request is made with a valid JWT token, the request should be processed, and when made with an invalid or missing token, the request should be rejected with an unauthorized error.
**Validates: Requirements 1.3**

**Property 4: Password hashing security**
*For any* user password, when stored in the database, the password should be hashed (not plain text), and the same password should produce different hashes when registered multiple times (due to salt).
**Validates: Requirements 1.5**

### Interview Management Properties

**Property 5: Interview creation and persistence**
*For any* role and number of questions, when an interview is created by an authenticated user, the system should: (1) generate the requested number of questions, (2) persist the interview with all questions to the database, (3) return an interview ID and all questions, and (4) associate the interview with the creating user.
**Validates: Requirements 2.1, 2.3, 2.4, 2.5**

**Property 6: Interview ownership validation**
*For any* interview, when queried, only the user who created it or participated in it should be able to access it, and other users should receive an authorization error.
**Validates: Requirements 6.5**

### Answer Submission Properties

**Property 7: Answer validation and persistence**
*For any* answer submission, when the interview and question exist, the answer should be persisted with correct associations to the interview, question, and user, and when the interview or question doesn't exist, a validation error should be returned.
**Validates: Requirements 3.1, 3.2, 3.5**

**Property 8: Non-blocking answer submission**
*For any* valid answer submission, the API should return an acknowledgment response within a short time threshold (e.g., < 500ms) without waiting for evaluation to complete.
**Validates: Requirements 3.4**

**Property 9: Evaluation pipeline triggering**
*For any* submitted answer, the evaluation pipeline should be triggered asynchronously, and the evaluation status should eventually transition from "pending" to either "completed" or "failed".
**Validates: Requirements 3.3, 4.1**

### Evaluation Properties

**Property 10: Evaluation result structure**
*For any* completed evaluation, the persisted result should be a valid JSON structure containing: (1) numerical scores for all required dimensions (correctness, completeness, quality, communication), (2) non-empty feedback text, and (3) a list of suggestions.
**Validates: Requirements 5.1, 5.2, 5.3, 5.5**

**Property 11: Evaluation structure validation**
*For any* evaluation result, when saving to the database, if the JSON structure is invalid (missing required fields, wrong types), the system should reject it with a validation error.
**Validates: Requirements 5.4**

**Property 12: Evaluation error handling**
*For any* evaluation that fails (LLM API error, timeout, parsing error), the system should log the error and mark the evaluation status as "failed" without crashing.
**Validates: Requirements 4.4**

**Property 13: Non-blocking evaluation processing**
*For any* ongoing evaluation, API endpoints should remain responsive and not block on evaluation completion.
**Validates: Requirements 4.5**

### Report Generation Properties

**Property 14: Report completeness**
*For any* interview with N questions, M submitted answers, and K completed evaluations, when a report is requested, it should contain all N questions, all M answers with their associations, and all K evaluation results.
**Validates: Requirements 6.1, 6.2, 6.3**

**Property 15: Report not found handling**
*For any* non-existent interview ID, when a report is requested, the system should return a 404 not found error.
**Validates: Requirements 6.4**

### Frontend Integration Properties

**Property 16: JWT token inclusion in requests**
*For any* authenticated API request from the frontend, the request should include the JWT token in the Authorization header.
**Validates: Requirements 10.1**

**Property 17: API response parsing and display**
*For any* successful API response, the frontend should correctly parse the JSON data and render it in the appropriate UI components without errors.
**Validates: Requirements 10.2**

**Property 18: API error handling**
*For any* failed API request, the frontend should display an appropriate error message to the user.
**Validates: Requirements 10.3**

**Property 19: Authentication error redirect**
*For any* API response with 401 unauthorized status, the frontend should redirect the user to the login page.
**Validates: Requirements 10.4**

**Property 20: Loading state display**
*For any* asynchronous operation (API call, data loading), the frontend should display a loading indicator while the operation is in progress and hide it when complete.
**Validates: Requirements 9.6**

**Property 21: Evaluation display completeness**
*For any* completed evaluation, the frontend should render: (1) all numerical scores prominently, (2) formatted feedback text, (3) suggestions as a list, and (4) visual indicators (colors, progress bars) based on score values.
**Validates: Requirements 11.1, 11.2, 11.3, 11.4**

**Property 22: Pending evaluation status display**
*For any* answer with a pending evaluation, the frontend should display a processing/pending status indicator.
**Validates: Requirements 11.5**

### Infrastructure Properties

**Property 23: Database connection error handling**
*For any* database connection failure, the system should handle it gracefully by logging the error and returning an appropriate error response without crashing.
**Validates: Requirements 8.5**

## Error Handling

### Backend Error Handling Strategy

**Authentication Errors:**
- Invalid credentials → 401 Unauthorized with message "Invalid username or password"
- Expired token → 401 Unauthorized with message "Token has expired"
- Missing token → 401 Unauthorized with message "Authentication required"
- Malformed token → 401 Unauthorized with message "Invalid token format"

**Validation Errors:**
- Invalid request body → 422 Unprocessable Entity with field-specific error messages
- Missing required fields → 422 Unprocessable Entity with list of missing fields
- Type mismatches → 422 Unprocessable Entity with expected vs actual type

**Resource Errors:**
- Interview not found → 404 Not Found with message "Interview not found"
- Question not found → 404 Not Found with message "Question not found"
- Answer not found → 404 Not Found with message "Answer not found"

**Authorization Errors:**
- Accessing another user's interview → 403 Forbidden with message "Access denied"
- Submitting answer to interview user didn't create → 403 Forbidden

**Database Errors:**
- Connection failure → 503 Service Unavailable with message "Database temporarily unavailable"
- Query timeout → 504 Gateway Timeout with message "Request timeout"
- Constraint violation → 409 Conflict with specific constraint message

**LLM Service Errors:**
- API key invalid → Log error, return 500 Internal Server Error
- Rate limit exceeded → Log error, mark evaluation as "failed", retry with exponential backoff
- Timeout → Log error, mark evaluation as "failed", allow manual retry
- Invalid response format → Log error, mark evaluation as "failed"

**Error Response Format:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "specific field error" // optional
    }
  }
}
```

### Frontend Error Handling Strategy

**Network Errors:**
- No internet connection → Display "No internet connection. Please check your network."
- Request timeout → Display "Request timed out. Please try again."
- Server unreachable → Display "Unable to reach server. Please try again later."

**API Errors:**
- 401 Unauthorized → Redirect to login page, clear stored token
- 403 Forbidden → Display "You don't have permission to access this resource."
- 404 Not Found → Display "Resource not found." with option to go back
- 422 Validation Error → Display field-specific errors inline in forms
- 500 Server Error → Display "Something went wrong. Please try again later."

**User Input Errors:**
- Empty required fields → Inline validation with red border and error message
- Invalid email format → "Please enter a valid email address"
- Password too short → "Password must be at least 8 characters"
- Answer too short → "Answer must be at least 10 characters"

**State Errors:**
- Failed to load data → Display error message with "Retry" button
- Failed to submit → Display error message, preserve user input, allow retry

### Error Logging

**Backend Logging:**
- Use Python `logging` module with structured logging
- Log levels: DEBUG (development), INFO (requests), WARNING (recoverable errors), ERROR (failures), CRITICAL (system failures)
- Log format: `[timestamp] [level] [module] [user_id] message`
- Log to stdout (captured by deployment platform)
- Include request ID for tracing

**Frontend Logging:**
- Console errors in development mode
- Send critical errors to backend logging endpoint (optional)
- Include user context (user ID, page, action) in error reports

## Testing Strategy

### Backend Testing

**Unit Tests:**
- Test individual service functions with mocked dependencies
- Test authentication functions (hash_password, verify_password, create_token, verify_token)
- Test LLM prompt building functions
- Test evaluation parsing functions
- Test database model methods
- Focus on edge cases: empty inputs, invalid formats, boundary values

**Property-Based Tests:**
- Use `hypothesis` library for Python property-based testing
- Configure each test to run minimum 100 iterations
- Tag each test with: `# Feature: ai-interview-platform, Property N: [property text]`

Property test examples:
```python
# Feature: ai-interview-platform, Property 1: Valid credentials produce valid JWT tokens
@given(username=st.text(min_size=3), password=st.text(min_size=8))
def test_valid_credentials_produce_tokens(username, password):
    # Create user, authenticate, verify token is valid
    pass

# Feature: ai-interview-platform, Property 5: Interview creation and persistence
@given(role=st.text(min_size=1), num_questions=st.integers(min_value=1, max_value=10))
def test_interview_creation_persistence(role, num_questions):
    # Create interview, verify persistence and associations
    pass

# Feature: ai-interview-platform, Property 10: Evaluation result structure
@given(evaluation_data=st.fixed_dictionaries({...}))
def test_evaluation_structure(evaluation_data):
    # Verify structure has all required fields with correct types
    pass
```

**Integration Tests:**
- Test complete API flows with test database
- Test authentication flow: register → login → access protected endpoint
- Test interview flow: create → submit answer → check evaluation → get report
- Test error scenarios: invalid tokens, missing resources, database failures
- Use `pytest-asyncio` for async test support
- Use `httpx.AsyncClient` for API testing

**Database Tests:**
- Test migrations run successfully
- Test relationships and cascading deletes
- Test unique constraints
- Test indexes improve query performance

### Frontend Testing

**Unit Tests:**
- Use Vitest for component testing
- Test individual components in isolation with mocked props
- Test utility functions (API client, token management)
- Test form validation logic
- Focus on edge cases and error states

**Property-Based Tests:**
- Use `fast-check` library for JavaScript property-based testing
- Configure each test to run minimum 100 iterations

Property test examples:
```javascript
// Feature: ai-interview-platform, Property 16: JWT token inclusion in requests
fc.assert(fc.property(fc.string(), async (token) => {
  // Make authenticated request, verify Authorization header present
}), { numRuns: 100 });

// Feature: ai-interview-platform, Property 21: Evaluation display completeness
fc.assert(fc.property(evaluationArbitrary, (evaluation) => {
  // Render evaluation, verify all elements present
}), { numRuns: 100 });
```

**Integration Tests:**
- Use React Testing Library for component integration
- Test page-level flows: login → dashboard → interview → report
- Test API integration with mocked backend (MSW - Mock Service Worker)
- Test error handling and loading states
- Test navigation and routing

**End-to-End Tests (Optional):**
- Use Playwright or Cypress for full system tests
- Test critical user journeys
- Run against staging environment before production deployment

### Testing Balance

- **Unit tests**: Specific examples, edge cases, error conditions (fast, isolated)
- **Property tests**: Universal properties across all inputs (comprehensive coverage)
- **Integration tests**: Component interactions, API contracts (realistic scenarios)
- Together these provide comprehensive coverage: unit tests catch concrete bugs, property tests verify general correctness, integration tests ensure components work together

### Test Coverage Goals

- Backend: 80%+ code coverage
- Frontend: 70%+ code coverage
- All correctness properties must have corresponding property-based tests
- All API endpoints must have integration tests
- All error paths must have unit tests

### Continuous Integration

- Run all tests on every commit
- Run property tests with 100 iterations in CI
- Run integration tests against test database
- Block merges if tests fail
- Generate coverage reports

## Deployment Architecture

### Backend Deployment (Render/Railway)

**Configuration:**
- Use Docker container or Python buildpack
- Set environment variables in platform dashboard
- Use managed PostgreSQL database service
- Enable auto-deploy from main branch

**Database Setup:**
- Create PostgreSQL instance on same platform
- Run migrations on deployment: `alembic upgrade head`
- Use connection pooling (SQLAlchemy default)
- Enable SSL for database connections

**Scaling Considerations:**
- Start with single instance (sufficient for MVP)
- Scale horizontally by adding instances (stateless design)
- Use Redis for background tasks if FastAPI BackgroundTasks insufficient
- Consider Celery + Redis for high-volume evaluation processing
- Database connection pool size: 20-50 connections per instance

**Health Checks:**
- Implement `/health` endpoint returning 200 OK
- Check database connectivity in health endpoint
- Platform monitors health endpoint for auto-restart

### Frontend Deployment (Vercel)

**Configuration:**
- Connect GitHub repository
- Set build command: `npm run build`
- Set output directory: `dist`
- Set environment variable: `VITE_API_BASE_URL`
- Enable auto-deploy from main branch

**Performance Optimizations:**
- Code splitting by route
- Lazy load components
- Optimize images
- Enable Vercel CDN caching
- Use Vercel Analytics for monitoring

### Environment Management

**Development:**
- Local PostgreSQL database
- Local backend on `localhost:8000`
- Local frontend on `localhost:5173`
- Use `.env.local` files (gitignored)

**Staging (Optional):**
- Separate database instance
- Staging backend deployment
- Staging frontend deployment
- Use for testing before production

**Production:**
- Production database with backups
- Production backend with monitoring
- Production frontend with CDN
- Use environment variables for all secrets

### Security Considerations

**Backend:**
- Never commit secrets to git
- Use strong SECRET_KEY for JWT (generate with `openssl rand -hex 32`)
- Enable CORS only for frontend domain
- Use HTTPS only (enforced by deployment platforms)
- Rate limit API endpoints (use `slowapi` library)
- Validate all inputs with Pydantic
- Use parameterized queries (SQLAlchemy ORM handles this)

**Frontend:**
- Store JWT in localStorage (acceptable for MVP, consider httpOnly cookies for production)
- Clear token on logout
- Don't expose API keys in frontend code
- Use environment variables for configuration
- Implement CSRF protection if using cookies

**Database:**
- Use strong passwords
- Enable SSL connections
- Regular backups (automated by platform)
- Restrict network access to backend only

### Monitoring and Observability

**Backend Monitoring:**
- Platform logs (stdout/stderr)
- Error tracking (optional: Sentry)
- Performance monitoring (optional: New Relic, DataDog)
- Database query performance (platform metrics)

**Frontend Monitoring:**
- Vercel Analytics (built-in)
- Error tracking (optional: Sentry)
- User analytics (optional: Google Analytics)

**Alerts:**
- High error rate
- Database connection failures
- LLM API failures
- High response times

### Backup and Recovery

**Database Backups:**
- Automated daily backups (platform feature)
- Point-in-time recovery capability
- Test restore process regularly

**Disaster Recovery:**
- Document deployment process
- Keep infrastructure as code (environment variables documented)
- Maintain database migration history
- Regular backup verification

## Scalability Considerations

### Current Architecture (MVP)

The initial architecture is designed for simplicity and rapid deployment:
- Single backend instance
- FastAPI BackgroundTasks for evaluation
- Managed PostgreSQL database
- Suitable for: 100s of concurrent users, 1000s of interviews/day

### Scaling Path

**Phase 1: Vertical Scaling (10x capacity)**
- Increase backend instance size (more CPU/RAM)
- Increase database instance size
- Add database read replicas for report queries
- Implement Redis caching for frequently accessed data

**Phase 2: Horizontal Scaling (100x capacity)**
- Multiple backend instances behind load balancer
- Separate background worker instances
- Replace FastAPI BackgroundTasks with Celery + Redis
- Implement distributed task queue
- Database connection pooling per instance
- Consider database sharding by user_id

**Phase 3: Service Decomposition (1000x capacity)**
- Separate evaluation service (microservice)
- Separate LLM service with caching
- Message queue (RabbitMQ/Kafka) for async communication
- Dedicated worker pool for evaluations
- CDN for static assets
- ElasticSearch for report search functionality

**Phase 4: Advanced Optimizations**
- Implement caching layer (Redis) for interviews and reports
- Use WebSockets for real-time evaluation updates
- Batch LLM requests for cost optimization
- Implement rate limiting per user
- Add analytics and monitoring dashboards
- Consider serverless functions for evaluation (AWS Lambda, Google Cloud Functions)

### Cost Optimization

**MVP Costs (estimated monthly):**
- Backend hosting: $7-20 (Render/Railway)
- Database: $7-15 (managed PostgreSQL)
- Frontend: $0 (Vercel free tier)
- LLM API: Variable ($0.01-0.10 per evaluation)
- Total: ~$15-50/month + LLM costs

**Optimization Strategies:**
- Cache LLM responses for identical questions/answers
- Batch evaluations to reduce API calls
- Use cheaper LLM models for initial screening
- Implement request deduplication
- Monitor and optimize database queries
- Use CDN for static assets (included in Vercel)

## Future Enhancements

**Feature Additions:**
- Real-time evaluation updates via WebSockets
- Interview templates and question banks
- Multi-language support
- Video/audio answer submission
- Collaborative interview reviews
- Interview scheduling and calendar integration
- Email notifications for evaluation completion
- Export reports to PDF
- Analytics dashboard for interviewers

**Technical Improvements:**
- Implement comprehensive logging and monitoring
- Add request tracing for debugging
- Implement API versioning
- Add GraphQL API option
- Implement webhook support for integrations
- Add admin panel for system management
- Implement A/B testing framework
- Add feature flags for gradual rollouts
