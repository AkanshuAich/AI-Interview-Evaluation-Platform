"""
Answer router for answer submission and evaluation status endpoints.

Endpoints:
    - POST /api/answers: Submit an answer and trigger background evaluation
    - GET /api/answers/{answer_id}/status: Check evaluation status for an answer

Requirements:
    - 3.1: Accept answer text for a specific question
    - 3.2: Validate answer belongs to valid interview/question
    - 3.3: Trigger background evaluation pipeline
    - 3.4: Return immediate acknowledgment without waiting for evaluation
    - 3.5: Enforce authorization (user must have access to interview)
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.answer import Answer
from app.models.evaluation import Evaluation
from app.schemas.answer_schemas import AnswerSubmit, AnswerResponse, EvaluationResponse
from app.services.auth_service import get_current_user
from app.services.answer_service import answer_service
from app.services.evaluation_service import evaluation_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/answers", tags=["answers"])


@router.post("", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    answer_data: AnswerSubmit,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an answer and trigger background evaluation.
    
    This endpoint:
    1. Validates the authenticated user has access to the interview
    2. Validates the question exists and belongs to the interview
    3. Persists the answer to the database
    4. Triggers background evaluation task (non-blocking)
    5. Returns immediate acknowledgment with answer ID
    
    Args:
        answer_data: Answer submission request (question_id, answer_text)
        background_tasks: FastAPI background tasks for async evaluation
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Created answer with ID, question_id, answer_text, and submitted_at
        
    Raises:
        HTTPException 401: If JWT token is invalid or expired
        HTTPException 403: If user doesn't have access to this interview
        HTTPException 404: If question not found
        HTTPException 422: If request validation fails
        HTTPException 500: If database error occurs
        
    Requirements:
        - 3.1: Accept answer text for a specific question
        - 3.2: Validate answer belongs to valid interview/question
        - 3.3: Trigger background evaluation pipeline
        - 3.4: Return immediate acknowledgment without waiting for evaluation
        - 3.5: Enforce authorization (user must have access to interview)
    """
    logger.info(
        f"User {current_user.id} submitting answer for question {answer_data.question_id}"
    )
    
    try:
        # Submit answer using answer service (includes validation and authorization)
        answer = await answer_service.submit_answer(
            db=db,
            user_id=current_user.id,
            interview_id=answer_data.interview_id,
            question_id=answer_data.question_id,
            answer_text=answer_data.answer_text
        )
        
        logger.info(
            f"Successfully created answer {answer.id} for question {answer_data.question_id}"
        )
        
        # Refresh to ensure all attributes are loaded
        await db.refresh(answer)
        
        # Trigger background evaluation task (non-blocking)
        # Note: We need to create a new DB session for the background task
        from app.core.database import AsyncSessionLocal
        
        async def run_evaluation():
            async with AsyncSessionLocal() as bg_db:
                await evaluation_service.evaluate_answer_async(bg_db, answer.id)
        
        background_tasks.add_task(run_evaluation)
        
        logger.info(f"Queued background evaluation for answer {answer.id}")
        
        # Return immediate acknowledgment (evaluation will be None initially)
        return AnswerResponse(
            id=answer.id,
            answer_text=answer.answer_text,
            submitted_at=answer.submitted_at,
            evaluation=None  # Evaluation is processed in background
        )
        
    except ValueError as e:
        # Validation error (question not found, authorization failed, etc.)
        logger.error(f"Validation error submitting answer: {e}")
        
        # Determine appropriate status code based on error message
        error_msg = str(e).lower()
        if "not found" in error_msg:
            status_code = status.HTTP_404_NOT_FOUND
        elif "access" in error_msg or "permission" in error_msg:
            status_code = status.HTTP_403_FORBIDDEN
        else:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        # Database error
        logger.error(f"Error submitting answer: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit answer. Please try again later."
        )


@router.get("/{answer_id}/status", response_model=dict)
async def get_answer_status(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check evaluation status for a submitted answer.
    
    Returns the answer with its evaluation status and results if available.
    Only the user who submitted the answer can check its status.
    
    Args:
        answer_id: ID of the answer to check
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Dictionary with:
        - answer: Answer details (id, question_id, answer_text, submitted_at)
        - evaluation_status: "pending", "completed", or "failed"
        - evaluation: Evaluation details if completed (scores, feedback, suggestions)
        
    Raises:
        HTTPException 401: If JWT token is invalid or expired
        HTTPException 403: If user doesn't have access to this answer
        HTTPException 404: If answer not found
        
    Requirements:
        - 3.4: Allow checking evaluation status
        - 4.3: Return evaluation results when available
    """
    logger.info(f"User {current_user.id} checking status for answer {answer_id}")
    
    try:
        # Fetch answer with authorization check
        result = await db.execute(
            select(Answer).where(Answer.id == answer_id)
        )
        answer = result.scalar_one_or_none()
        
        if answer is None:
            logger.warning(f"Answer {answer_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        # Check authorization: user must own the answer
        if answer.user_id != current_user.id:
            logger.warning(
                f"User {current_user.id} denied access to answer {answer_id} "
                f"owned by user {answer.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this answer"
            )
        
        # Fetch evaluation if it exists
        result = await db.execute(
            select(Evaluation).where(Evaluation.answer_id == answer_id)
        )
        evaluation = result.scalar_one_or_none()
        
        # Build response manually to avoid lazy loading issues
        response = {
            "answer": {
                "id": answer.id,
                "answer_text": answer.answer_text,
                "submitted_at": answer.submitted_at.isoformat(),
                "evaluation": None
            },
            "evaluation_status": "pending",
            "evaluation": None
        }
        
        if evaluation:
            response["evaluation_status"] = evaluation.status
            if evaluation.status == "completed":
                response["evaluation"] = {
                    "scores": evaluation.scores,
                    "feedback": evaluation.feedback,
                    "suggestions": evaluation.suggestions,
                    "evaluated_at": evaluation.evaluated_at.isoformat(),
                    "status": evaluation.status
                }
        
        logger.info(
            f"Returning status for answer {answer_id}: {response['evaluation_status']}"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Database error
        logger.error(f"Error checking answer status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check answer status. Please try again later."
        )
