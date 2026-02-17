"""
Report service for fetching complete interview reports with evaluations.

This service handles:
- Fetching interview with all questions, answers, and evaluations
- Calculating overall interview scores
- Authorization checks for report access

Requirements:
    - 6.1: Fetch interview with all questions, answers, and evaluations
    - 6.2: Calculate overall interview score
    - 6.3: Return structured report data
    - 6.5: Enforce authorization (user must own interview)
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.interview import Interview
from app.models.question import Question
from app.models.answer import Answer
from app.models.evaluation import Evaluation


logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating interview reports."""
    
    async def get_interview_report(
        self,
        db: AsyncSession,
        interview_id: int,
        user_id: int
    ) -> Optional[Interview]:
        """
        Fetch complete interview report with all questions, answers, and evaluations.
        
        This method:
        1. Fetches the interview with authorization check
        2. Eagerly loads all related questions, answers, and evaluations
        3. Returns the complete interview object for report generation
        
        Args:
            db: Database session
            interview_id: ID of the interview to fetch
            user_id: ID of the user requesting the report
            
        Returns:
            Interview object with all related data, or None if not found/unauthorized
            
        Raises:
            ValueError: If user doesn't have access to this interview
            
        Requirements:
            - 6.1: Fetch interview with all questions, answers, and evaluations
            - 6.5: Enforce authorization (user must own interview)
        """
        logger.info(f"Fetching report for interview {interview_id}, user {user_id}")
        
        # Fetch interview with all related data using eager loading
        result = await db.execute(
            select(Interview)
            .where(Interview.id == interview_id)
            .options(
                selectinload(Interview.questions)
                .selectinload(Question.answers)
                .selectinload(Answer.evaluation)
            )
        )
        interview = result.scalar_one_or_none()
        
        if interview is None:
            logger.warning(f"Interview {interview_id} not found")
            return None
        
        # Check authorization: user must own the interview
        if interview.user_id != user_id:
            logger.warning(
                f"User {user_id} denied access to interview {interview_id} "
                f"owned by user {interview.user_id}"
            )
            raise ValueError("You don't have permission to access this interview")
        
        logger.info(
            f"Successfully fetched report for interview {interview_id} "
            f"with {len(interview.questions)} questions"
        )
        
        return interview
    
    def calculate_overall_score(self, interview: Interview) -> Optional[float]:
        """
        Calculate overall interview score from individual evaluations.
        
        The overall score is the average of all completed evaluation scores.
        Each evaluation score is the average of correctness, completeness, quality, and communication.
        
        Args:
            interview: Interview object with questions, answers, and evaluations
            
        Returns:
            Overall score (0-10) or None if no completed evaluations exist
            
        Requirements:
            - 6.2: Calculate overall interview score from individual evaluations
        """
        logger.info(f"Calculating overall score for interview {interview.id}")
        
        evaluation_scores = []
        
        # Iterate through all questions and their answers
        for question in interview.questions:
            for answer in question.answers:
                # Only include completed evaluations
                if answer.evaluation and answer.evaluation.status == "completed":
                    # Extract scores from JSONB field
                    scores = answer.evaluation.scores
                    
                    # Calculate average score for this evaluation
                    # scores format: {"correctness": float, "completeness": float, "quality": float, "communication": float}
                    eval_score = (
                        scores.get("correctness", 0) +
                        scores.get("completeness", 0) +
                        scores.get("quality", 0) +
                        scores.get("communication", 0)
                    ) / 4.0
                    evaluation_scores.append(eval_score)
        
        if not evaluation_scores:
            logger.info(f"No completed evaluations found for interview {interview.id}")
            return None
        
        # Calculate overall average
        overall_score = sum(evaluation_scores) / len(evaluation_scores)
        
        logger.info(
            f"Overall score for interview {interview.id}: {overall_score:.2f} "
            f"(from {len(evaluation_scores)} evaluations)"
        )
        
        return round(overall_score, 2)


# Singleton instance
report_service = ReportService()
