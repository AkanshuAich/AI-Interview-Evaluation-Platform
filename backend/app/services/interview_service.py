"""
Interview service for managing interview creation and retrieval.
Handles business logic for interview operations including LLM integration.

Requirements:
    - 2.1: Generate relevant technical questions for specified roles
    - 2.3: Persist interview with generated questions to database
    - 2.4: Return interview ID and questions to client
    - 2.5: Associate interview with authenticated user
"""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.interview import Interview
from app.models.question import Question
from app.services.llm_service import llm_service


logger = logging.getLogger(__name__)


class InterviewService:
    """
    Service for interview management operations.
    
    Handles:
    - Creating interviews with LLM-generated questions
    - Retrieving user's interviews
    - Fetching specific interviews with authorization
    """
    
    async def create_interview(
        self,
        db: AsyncSession,
        user_id: int,
        role: str,
        num_questions: int
    ) -> Interview:
        """
        Create a new interview with LLM-generated questions.
        
        This method:
        1. Calls LLM service to generate questions for the role
        2. Creates an Interview record in the database
        3. Creates Question records associated with the interview
        4. Returns the complete interview with questions
        
        Args:
            db: Database session
            user_id: ID of the user creating the interview
            role: Job role for which to generate questions
            num_questions: Number of questions to generate (1-10)
            
        Returns:
            Interview object with questions loaded
            
        Raises:
            ValueError: If num_questions is out of range
            httpx exceptions: If LLM API call fails
            
        Requirements:
            - 2.1: Generate relevant technical questions for specified roles
            - 2.3: Persist interview with generated questions to database
            - 2.4: Return interview ID and questions to client
            - 2.5: Associate interview with authenticated user
        """
        logger.info(f"Creating interview for user {user_id}, role: {role}, questions: {num_questions}")
        
        # Generate questions using LLM service
        try:
            question_texts = await llm_service.generate_questions(role, num_questions)
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            raise
        
        # Create interview record
        interview = Interview(
            user_id=user_id,
            role=role
        )
        db.add(interview)
        await db.flush()  # Flush to get interview.id
        
        # Create question records
        questions = []
        for order, question_text in enumerate(question_texts, start=1):
            question = Question(
                interview_id=interview.id,
                question_text=question_text,
                question_order=order
            )
            questions.append(question)
            db.add(question)
        
        # Commit transaction
        await db.commit()
        
        # Refresh to load relationships
        await db.refresh(interview, ["questions"])
        
        logger.info(f"Successfully created interview {interview.id} with {len(questions)} questions")
        return interview
    
    async def get_user_interviews(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[Interview]:
        """
        Fetch all interviews created by a specific user.
        
        Args:
            db: Database session
            user_id: ID of the user whose interviews to fetch
            
        Returns:
            List of Interview objects with questions loaded, ordered by creation date (newest first)
            
        Requirements:
            - 2.5: Retrieve interviews associated with user
        """
        logger.info(f"Fetching interviews for user {user_id}")
        
        # Query interviews with questions eagerly loaded
        stmt = (
            select(Interview)
            .where(Interview.user_id == user_id)
            .options(selectinload(Interview.questions))
            .order_by(Interview.created_at.desc())
        )
        
        result = await db.execute(stmt)
        interviews = result.scalars().all()
        
        logger.info(f"Found {len(interviews)} interviews for user {user_id}")
        return list(interviews)
    
    async def get_interview_by_id(
        self,
        db: AsyncSession,
        interview_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Interview]:
        """
        Fetch a specific interview by ID with optional authorization check.
        
        Args:
            db: Database session
            interview_id: ID of the interview to fetch
            user_id: Optional user ID for authorization check
            
        Returns:
            Interview object with questions loaded, or None if not found or unauthorized
            
        Requirements:
            - 2.4: Fetch specific interview
            - 6.5: Authorization check for interview access
        """
        logger.info(f"Fetching interview {interview_id}")
        
        # Query interview with questions eagerly loaded
        stmt = (
            select(Interview)
            .where(Interview.id == interview_id)
            .options(selectinload(Interview.questions))
        )
        
        result = await db.execute(stmt)
        interview = result.scalar_one_or_none()
        
        if interview is None:
            logger.warning(f"Interview {interview_id} not found")
            return None
        
        # Authorization check if user_id provided
        if user_id is not None and interview.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access interview {interview_id} "
                f"owned by user {interview.user_id}"
            )
            return None
        
        logger.info(f"Successfully fetched interview {interview_id}")
        return interview


# Global interview service instance
interview_service = InterviewService()
