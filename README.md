# AI Interview Evaluation Platform

A full-stack web application that conducts AI-powered technical interviews with automated evaluation and detailed feedback.

## Overview

This platform allows users to:
- Create customized technical interviews for specific job roles
- Answer interview questions through a web interface
- Receive AI-powered evaluations with detailed feedback
- View comprehensive reports with scores and improvement suggestions

## Architecture

```
AI-Interview-Platform/
├── backend/          # FastAPI backend with PostgreSQL
│   ├── app/
│   │   ├── core/     # Configuration and database
│   │   ├── models/   # SQLAlchemy models
│   │   ├── routers/  # API endpoints
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   ├── alembic/      # Database migrations
│   └── tests/        # Test suite
│
└── frontend/         # React + Vite frontend
    ├── src/
    │   ├── components/ # Reusable components
    │   ├── pages/      # Page components
    │   ├── services/   # API client
    │   └── utils/      # Utility functions
    └── public/         # Static assets
```

## Technology Stack

### Backend
- **FastAPI**: Modern async web framework
- **PostgreSQL**: Primary database with async support
- **SQLAlchemy 2.0**: Async ORM
- **Alembic**: Database migrations
- **Google Gemini / OpenAI API**: LLM for question generation and evaluation
- **JWT**: Authentication
- **Python 3.12**: Runtime environment

### Frontend
- **React 18**: UI library
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **TailwindCSS**: Utility-first CSS framework

## Features

### 1. User Authentication
- Secure registration and login
- JWT-based authentication
- Protected routes

### 2. Interview Creation
- Specify job role and number of questions
- AI generates relevant technical questions
- Questions stored with interview metadata

### 3. Interview Taking
- Display questions one by one
- Submit answers for each question
- Real-time evaluation status updates

### 4. AI Evaluation
- Background processing of answers
- Evaluation on multiple criteria:
  - Technical Accuracy
  - Completeness
  - Clarity
- Detailed feedback and suggestions

### 5. Comprehensive Reports
- View all questions with answers
- Visual score representation
- Detailed feedback for each answer
- Overall interview score
- Improvement suggestions

## Setup Instructions

### Prerequisites
- Python 3.12 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Google Gemini API key (free) or OpenAI API key

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```bash
   createdb ai_interview
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
   - `LLM_PROVIDER`: Choose "gemini" or "openai"
   - `LLM_API_KEY`: Your Gemini API key (get from https://makersuite.google.com/app/apikey) or OpenAI API key
   - `LLM_MODEL`: Model name (e.g., "gemini-1.5-flash" or "gpt-4")

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   API will be available at `http://localhost:8000`
   API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with backend URL
   ```

   Required variables:
   - `VITE_API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   App will be available at `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Interviews
- `POST /api/interviews` - Create new interview
- `GET /api/interviews` - List user's interviews
- `GET /api/interviews/{id}` - Get specific interview

### Answers
- `POST /api/answers` - Submit answer
- `GET /api/answers/{id}/status` - Check evaluation status

### Reports
- `GET /api/reports/{id}` - Get complete interview report

## Deployment

### Quick Deploy to Render (Free)

The easiest way to deploy this application is using **Render**, which supports both frontend and backend on one platform.

**Quick Steps:**

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/ai-interview-platform.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Sign up at https://render.com (free)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` and deploy everything
   - Add your `LLM_API_KEY` in the backend environment variables

3. **Done!** Your app will be live at:
   - Frontend: `https://your-app-frontend.onrender.com`
   - Backend: `https://your-app-backend.onrender.com`

**📖 For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)**

### What Gets Deployed:
- ✅ Backend API (FastAPI + Python)
- ✅ Frontend (React + Vite)
- ✅ PostgreSQL Database
- ✅ Automatic SSL certificates
- ✅ Auto-deploy on git push

### Free Tier Includes:
- 750 hours/month web service
- Unlimited static sites
- 1GB PostgreSQL database
- Note: Backend spins down after 15 min inactivity (30-60s cold start)

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test:**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend (manual testing)
   cd frontend
   npm run dev
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

## Testing

### Backend Tests
```bash
cd backend
pytest                          # Run all tests
pytest --cov=app               # Run with coverage
pytest tests/test_auth.py      # Run specific test file
```

### Frontend Testing
Manual testing through the UI. Automated tests can be added using Vitest or React Testing Library.

## Environment Variables

### Backend
| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| SECRET_KEY | JWT signing secret | Yes |
| LLM_PROVIDER | LLM provider ("gemini" or "openai") | Yes |
| LLM_API_KEY | Gemini or OpenAI API key | Yes |
| LLM_MODEL | Model name (e.g., "gemini-1.5-flash" or "gpt-4") | Yes |
| ALGORITHM | JWT algorithm | No (default: HS256) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration | No (default: 30) |
| LLM_API_URL | LLM API endpoint | No |
| CORS_ORIGINS | Allowed frontend origins | No |

### Frontend
| Variable | Description | Required |
|----------|-------------|----------|
| VITE_API_BASE_URL | Backend API base URL | Yes |

## Troubleshooting

### Backend Issues
- **Database connection errors**: Verify PostgreSQL is running and DATABASE_URL is correct
- **Migration errors**: Check all models are imported in `alembic/env.py`
- **Import errors**: Ensure virtual environment is activated

### Frontend Issues
- **API connection errors**: Verify backend is running and VITE_API_BASE_URL is correct
- **Build errors**: Clear node_modules and reinstall dependencies
- **Authentication issues**: Clear localStorage and verify backend auth endpoints

## Future Enhancements

- User profile management
- Interview templates
- Multiple LLM provider support
- Real-time collaboration
- Interview scheduling
- Analytics dashboard
- Export reports to PDF
- Video interview integration
- Code execution for programming questions

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs`

## Acknowledgments

- OpenAI for LLM API
- FastAPI framework
- React and Vite teams
- TailwindCSS team
