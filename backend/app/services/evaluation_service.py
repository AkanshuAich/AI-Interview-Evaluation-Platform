"""
Evaluation service for background processing of answer evaluations.
Handles asynchronous evaluation of answers using LLM service.

Requirements:
    - 3.3: Trigger evaluation pipeline asynchronously
    - 4.1: Process evaluation in background
    - 4.3: Persist evaluation to database with status tracking
    - 4.4: Handle errors and mark evaluation as failed
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.answer import Answer
from app.models.question import Question
from app.models.interview import Interview
from app.models.evaluation import Evaluation
from app.services.llm_service import llm_service, EvaluationResult


logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Service for managing answer evaluation operations.
    
    Handles:
    - Background evaluation of answers using LLM
    - Parsing and validating evaluation responses
    - Persisting evaluations to database with status tracking
    - Error handling for failed evaluations
    """
    
    async def evaluate_answer_async(
        self,
        db: AsyncSession,
        answer_id: int
    ) -> None:
        """
        Background task to evaluate an answer using the LLM service.
        
        This method:
        1. Fetches the answer with its question and interview context
        2. Calls the LLM service to evaluate the answer
        3. Parses and validates the evaluation response
        4. Persists the evaluation to the database with status "completed"
        5. Handles errors by marking evaluation as "failed"
        
        This is designed to be run as a background task and does not return
        a value. It commits its own database transaction.
        
        Args:
            db: Database session
            answer_id: ID of the answer to evaluate
            
        Requirements:
            - 3.3: Trigger evaluation pipeline asynchronously
            - 4.1: Process evaluation in background
            - 4.3: Persist evaluation to database with status tracking
            - 4.4: Handle errors and mark evaluation as failed
        """
        logger.info(f"Starting background evaluation for answer {answer_id}")
        
        try:
            # Fetch answer with question and interview context
            stmt = (
                select(Answer)
                .where(Answer.id == answer_id)
                .options(
                    selectinload(Answer.question).selectinload(Question.interview)
                )
            )
            result = await db.execute(stmt)
            answer = result.scalar_one_or_none()
            
            if answer is None:
                logger.error(f"Answer {answer_id} not found for evaluation")
                return
            
            # Get question and interview context
            question = answer.question
            interview = question.interview
            
            logger.info(
                f"Evaluating answer {answer_id} for question {question.id} "
                f"in interview {interview.id} (role: {interview.role})"
            )
            
            # Call LLM service to evaluate the answer
            evaluation_result = await llm_service.evaluate_answer(
                question=question.question_text,
                answer=answer.answer_text,
                role=interview.role
            )
            
            # Save evaluation to database
            await self._save_evaluation(
                db=db,
                answer_id=answer_id,
                evaluation_result=evaluation_result,
                status="completed"
            )
            
            logger.info(f"Successfully completed evaluation for answer {answer_id}")
            
        except Exception as e:
            # Log error and mark evaluation as failed
            logger.error(
                f"Evaluation failed for answer {answer_id}: {type(e).__name__}: {e}",
                exc_info=True
            )
            
            try:
                # Create a failed evaluation record
                await self._save_failed_evaluation(
                    db=db,
                    answer_id=answer_id,
                    error_message=str(e)
                )
            except Exception as save_error:
                logger.error(
                    f"Failed to save error status for answer {answer_id}: {save_error}",
                    exc_info=True
                )
    
    async def _save_evaluation(
        self,
        db: AsyncSession,
        answer_id: int,
        evaluation_result: EvaluationResult,
        status: str
    ) -> Evaluation:
        """
        Save evaluation result to the database.
        
        Args:
            db: Database session
            answer_id: ID of the answer being evaluated
            evaluation_result: Parsed evaluation result from LLM
            status: Evaluation status ("completed" or "failed")
            
        Returns:
            Created Evaluation object
            
        Requirements:
            - 4.3: Persist evaluation to database with status tracking
        """
        # Convert Pydantic models to dict for JSON storage
        scores_dict = evaluation_result.scores.model_dump()
        suggestions_list = evaluation_result.suggestions
        
        # Create evaluation record
        evaluation = Evaluation(
            answer_id=answer_id,
            scores=scores_dict,
            feedback=evaluation_result.feedback,
            suggestions=suggestions_list,
            status=status
        )
        
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        
        logger.info(f"Saved evaluation {evaluation.id} for answer {answer_id}")
        return evaluation
    
    async def _save_failed_evaluation(
        self,
        db: AsyncSession,
        answer_id: int,
        error_message: str
    ) -> Evaluation:
        """
        Save a failed evaluation record to the database.
        
        Creates an evaluation record with status "failed" and minimal data
        to track that the evaluation was attempted but failed.
        
        Args:
            db: Database session
            answer_id: ID of the answer that failed evaluation
            error_message: Error message describing the failure
            
        Returns:
            Created Evaluation object with failed status
            
        Requirements:
            - 4.4: Handle errors and mark evaluation as failed
        """
        # Create minimal evaluation record for failed status
        evaluation = Evaluation(
            answer_id=answer_id,
            scores={
                "correctness": 0.0,
                "completeness": 0.0,
                "quality": 0.0,
                "communication": 0.0
            },
            feedback=f"Evaluation failed: {error_message}",
            suggestions=["Please retry the evaluation or contact support."],
            status="failed"
        )
        
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        
        logger.info(f"Saved failed evaluation {evaluation.id} for answer {answer_id}")
        return evaluation
    
    async def get_evaluation_status(
        self,
        db: AsyncSession,
        answer_id: int
    ) -> Optional[dict]:
        """
        Get the evaluation status for an answer.
        
        Args:
            db: Database session
            answer_id: ID of the answer
            
        Returns:
            Dictionary with evaluation status and data, or None if no evaluation exists
        """
        stmt = select(Evaluation).where(Evaluation.answer_id == answer_id)
        result = await db.execute(stmt)
        evaluation = result.scalar_one_or_none()
        
        if evaluation is None:
            return {
                "status": "pending",
                "evaluation": None
            }
        
        return {
            "status": evaluation.status,
            "evaluation": {
                "scores": evaluation.scores,
                "feedback": evaluation.feedback,
                "suggestions": evaluation.suggestions,
                "evaluated_at": evaluation.evaluated_at.isoformat()
            } if evaluation.status == "completed" else None
        }


# Global evaluation service instance
evaluation_service = EvaluationService()
