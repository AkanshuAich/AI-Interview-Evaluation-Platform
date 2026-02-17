"""
Report router for fetching complete interview reports.

Endpoints:
    - GET /api/reports/{interview_id}: Get complete interview report with all questions, answers, and evaluations

Requirements:
    - 6.1: Fetch interview with all questions, answers, and evaluations
    - 6.2: Calculate overall interview score
    - 6.3: Return structured report data
    - 6.4: Handle not found errors
    - 6.5: Enforce authorization (user must own interview)
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.answer import Answer
from app.schemas.report_schemas import InterviewReport, QuestionWithAnswer
from app.schemas.answer_schemas import AnswerResponse, EvaluationResponse
from app.services.auth_service import get_current_user
from app.services.report_service import report_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{interview_id}", response_model=InterviewReport)
async def get_interview_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete interview report with all questions, answers, and evaluations.
    
    This endpoint:
    1. Validates the authenticated user has access to the interview
    2. Fetches the interview with all related data
    3. Calculates the overall interview score
    4. Returns a structured report with all questions, answers, and evaluations
    
    Args:
        interview_id: ID of the interview to fetch
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Complete interview report with:
        - Interview metadata (id, role, created_at)
        - All questions with their answers and evaluations
        - Overall score (average of all evaluation scores)
        
    Raises:
        HTTPException 401: If JWT token is invalid or expired
        HTTPException 403: If user doesn't have access to this interview
        HTTPException 404: If interview not found
        HTTPException 500: If database error occurs
        
    Requirements:
        - 6.1: Fetch interview with all questions, answers, and evaluations
        - 6.2: Calculate overall interview score
        - 6.3: Return structured report data
        - 6.4: Handle not found errors
        - 6.5: Enforce authorization (user must own interview)
    """
    logger.info(f"User {current_user.id} requesting report for interview {interview_id}")
    
    try:
        # Fetch interview with all related data
        interview = await report_service.get_interview_report(
            db=db,
            interview_id=interview_id,
            user_id=current_user.id
        )
        
        if interview is None:
            logger.warning(f"Interview {interview_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Calculate overall score
        overall_score = report_service.calculate_overall_score(interview)
        
        # Build report response
        questions_with_answers = []
        for question in sorted(interview.questions, key=lambda q: q.question_order):
            # Find answer for this question (if exists)
            answer_data = None
            if question.answers:
                # Get the first answer (should only be one per question per user)
                answer = question.answers[0]
                
                # Build answer response with evaluation
                answer_dict = {
                    "id": answer.id,
                    "question_id": answer.question_id,
                    "answer_text": answer.answer_text,
                    "submitted_at": answer.submitted_at
                }
                
                # Add evaluation if it exists and is completed
                if answer.evaluation:
                    # Extract scores from JSONB field
                    scores = answer.evaluation.scores
                    
                    evaluation_dict = {
                        "id": answer.evaluation.id,
                        "answer_id": answer.evaluation.answer_id,
                        "status": answer.evaluation.status,
                        "scores": scores,
                        "feedback": answer.evaluation.feedback,
                        "suggestions": answer.evaluation.suggestions,
                        "evaluated_at": answer.evaluation.evaluated_at
                    }
                    answer_dict["evaluation"] = evaluation_dict
                
                answer_data = answer_dict
            
            # Build question with answer
            question_with_answer = {
                "question_id": question.id,
                "question_text": question.question_text,
                "question_order": question.question_order,
                "answer": answer_data
            }
            questions_with_answers.append(question_with_answer)
        
        # Build report
        report = {
            "interview_id": interview.id,
            "role": interview.role,
            "created_at": interview.created_at,
            "questions": questions_with_answers,
            "overall_score": overall_score
        }
        
        logger.info(
            f"Successfully generated report for interview {interview_id} "
            f"with {len(questions_with_answers)} questions, overall score: {overall_score}"
        )
        
        return InterviewReport(**report)
        
    except ValueError as e:
        # Authorization error
        logger.error(f"Authorization error fetching report: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Database error
        logger.error(f"Error fetching report for interview {interview_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch interview report. Please try again later."
        )
