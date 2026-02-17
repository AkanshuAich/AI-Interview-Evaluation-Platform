"""
Interview router for interview creation and retrieval endpoints.

Endpoints:
    - POST /api/interviews: Create a new interview with LLM-generated questions
    - GET /api/interviews: List all interviews for the authenticated user
    - GET /api/interviews/{interview_id}: Get a specific interview with authorization

Requirements:
    - 2.1: Generate relevant technical questions for specified roles
    - 2.3: Persist interview with generated questions to database
    - 2.4: Return interview ID and questions to client
    - 2.5: Associate interview with authenticated user
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.schemas.interview_schemas import InterviewCreate, InterviewResponse
from app.services.auth_service import get_current_user
from app.services.interview_service import interview_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new interview with LLM-generated questions.
    
    This endpoint:
    1. Validates the authenticated user
    2. Calls the LLM service to generate role-specific questions
    3. Persists the interview and questions to the database
    4. Returns the complete interview with all questions
    
    Args:
        interview_data: Interview creation request (role, num_questions)
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Created interview with ID, role, timestamp, and questions
        
    Raises:
        HTTPException 401: If JWT token is invalid or expired
        HTTPException 422: If request validation fails
        HTTPException 500: If LLM service fails or database error occurs
        
    Requirements:
        - 2.1: Generate relevant technical questions for specified roles
        - 2.3: Persist interview with generated questions to database
        - 2.4: Return interview ID and questions to client
        - 2.5: Associate interview with authenticated user
    """
    logger.info(
        f"User {current_user.id} creating interview for role: {interview_data.role}, "
        f"questions: {interview_data.num_questions}"
    )
    
    try:
        # Create interview using interview service
        interview = await interview_service.create_interview(
            db=db,
            user_id=current_user.id,
            role=interview_data.role,
            num_questions=interview_data.num_questions
        )
        
        logger.info(f"Successfully created interview {interview.id} for user {current_user.id}")
        
        # Return interview response
        return InterviewResponse.model_validate(interview)
        
    except ValueError as e:
        # Invalid input parameters
        logger.error(f"Validation error creating interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        # LLM service failure or database error
        logger.error(f"Error creating interview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview. Please try again later."
        )


@router.get("", response_model=List[InterviewResponse])
async def list_interviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all interviews created by the authenticated user.
    
    Returns interviews ordered by creation date (newest first).
    Each interview includes its associated questions.
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        List of interviews with questions, ordered by created_at descending
        
    Raises:
        HTTPException 401: If JWT token is invalid or expired
        
    Requirements:
        - 2.5: Retrieve interviews associated with authenticated user
    """
    logger.info(f"User {current_user.id} listing their interviews")
    
    try:
        # Fetch user's interviews
        interviews = await interview_service.get_user_interviews(
            db=db,
            user_id=current_user.id
        )
        
        logger.info(f"Returning {len(interviews)} interviews for user {current_user.id}")
        
        # Convert to response models
        return [InterviewResponse.model_validate(interview) for interview in interviews]
        
    except Exception as e:
        # Database error
        logger.error(f"Error listing interviews: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interviews. Please try again later."
        )


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific interview by ID with authorization check.
    
    Only the user who created the interview can access it.
    Returns the interview with all associated questions.
    
    Args:
        interview_id: ID of the interview to retrieve
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        Interview with questions
        
    Raises:
        HTTPException 401: If JWT token is invalid or expired
        HTTPException 403: If user doesn't have access to this interview
        HTTPException 404: If interview not found
        
    Requirements:
        - 2.4: Fetch specific interview
        - 6.5: Authorization check for interview access
    """
    logger.info(f"User {current_user.id} requesting interview {interview_id}")
    
    try:
        # Fetch interview with authorization check
        interview = await interview_service.get_interview_by_id(
            db=db,
            interview_id=interview_id,
            user_id=current_user.id
        )
        
        if interview is None:
            # Interview not found or user doesn't have access
            # Check if interview exists at all to provide appropriate error
            interview_exists = await interview_service.get_interview_by_id(
                db=db,
                interview_id=interview_id,
                user_id=None  # No authorization check
            )
            
            if interview_exists is None:
                logger.warning(f"Interview {interview_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interview not found"
                )
            else:
                logger.warning(
                    f"User {current_user.id} denied access to interview {interview_id} "
                    f"owned by user {interview_exists.user_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access this interview"
                )
        
        logger.info(f"Successfully retrieved interview {interview_id} for user {current_user.id}")
        
        # Return interview response
        return InterviewResponse.model_validate(interview)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Database error
        logger.error(f"Error retrieving interview {interview_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview. Please try again later."
        )
