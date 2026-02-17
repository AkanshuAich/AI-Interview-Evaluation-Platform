"""
Answer service for managing answer submission and retrieval.
Handles business logic for answer operations including validation and authorization.

Requirements:
    - 3.1: Validate answer belongs to existing interview
    - 3.2: Persist answer to database
    - 3.5: Associate answer with correct interview and question
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.answer import Answer
from app.models.question import Question
from app.models.interview import Interview


logger = logging.getLogger(__name__)


class AnswerService:
    """
    Service for answer management operations.
    
    Handles:
    - Submitting answers with validation
    - Retrieving answers with evaluations
    - Authorization checks for interview access
    """
    
    async def submit_answer(
        self,
        db: AsyncSession,
        interview_id: int,
        question_id: int,
        answer_text: str,
        user_id: int
    ) -> Answer:
        """
        Submit an answer to an interview question.
        
        This method:
        1. Validates that the interview exists
        2. Validates that the question exists and belongs to the interview
        3. Validates that the user has access to the interview
        4. Creates and persists the answer
        5. Returns the answer (evaluation will be triggered separately)
        
        Args:
            db: Database session
            interview_id: ID of the interview
            question_id: ID of the question being answered
            answer_text: The candidate's answer text
            user_id: ID of the user submitting the answer
            
        Returns:
            Answer object
            
        Raises:
            ValueError: If interview/question doesn't exist or validation fails
            PermissionError: If user doesn't have access to the interview
            
        Requirements:
            - 3.1: Validate answer belongs to existing interview
            - 3.2: Persist answer to database
            - 3.5: Associate answer with correct interview and question
        """
        logger.info(
            f"Submitting answer for user {user_id}, interview {interview_id}, "
            f"question {question_id}"
        )
        
        # Validate interview exists
        interview_stmt = select(Interview).where(Interview.id == interview_id)
        interview_result = await db.execute(interview_stmt)
        interview = interview_result.scalar_one_or_none()
        
        if interview is None:
            logger.warning(f"Interview {interview_id} not found")
            raise ValueError(f"Interview {interview_id} does not exist")
        
        # Authorization check: user must have access to the interview
        # For now, we allow the interview creator to submit answers
        # In a real system, you might have separate candidate users
        if interview.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to submit answer to interview {interview_id} "
                f"owned by user {interview.user_id}"
            )
            raise PermissionError(
                f"User does not have access to interview {interview_id}"
            )
        
        # Validate question exists and belongs to the interview
        question_stmt = select(Question).where(Question.id == question_id)
        question_result = await db.execute(question_stmt)
        question = question_result.scalar_one_or_none()
        
        if question is None:
            logger.warning(f"Question {question_id} not found")
            raise ValueError(f"Question {question_id} does not exist")
        
        if question.interview_id != interview_id:
            logger.warning(
                f"Question {question_id} does not belong to interview {interview_id} "
                f"(belongs to interview {question.interview_id})"
            )
            raise ValueError(
                f"Question {question_id} does not belong to interview {interview_id}"
            )
        
        # Create answer record
        answer = Answer(
            question_id=question_id,
            user_id=user_id,
            answer_text=answer_text
        )
        db.add(answer)
        
        # Commit transaction
        await db.commit()
        await db.refresh(answer)
        
        logger.info(f"Successfully created answer {answer.id}")
        return answer
    
    async def get_answer_with_evaluation(
        self,
        db: AsyncSession,
        answer_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Answer]:
        """
        Fetch an answer with its evaluation results.
        
        Args:
            db: Database session
            answer_id: ID of the answer to fetch
            user_id: Optional user ID for authorization check
            
        Returns:
            Answer object with evaluation loaded, or None if not found or unauthorized
            
        Requirements:
            - Retrieve answer with evaluation for status checking
        """
        logger.info(f"Fetching answer {answer_id}")
        
        # Query answer with evaluation eagerly loaded
        stmt = (
            select(Answer)
            .where(Answer.id == answer_id)
            .options(selectinload(Answer.evaluation))
        )
        
        result = await db.execute(stmt)
        answer = result.scalar_one_or_none()
        
        if answer is None:
            logger.warning(f"Answer {answer_id} not found")
            return None
        
        # Authorization check if user_id provided
        if user_id is not None and answer.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access answer {answer_id} "
                f"owned by user {answer.user_id}"
            )
            return None
        
        logger.info(f"Successfully fetched answer {answer_id}")
        return answer


# Global answer service instance
answer_service = AnswerService()
