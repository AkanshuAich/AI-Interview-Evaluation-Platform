"""
LLM service for AI-powered interview question generation and answer evaluation.
Uses OpenAI API (or compatible endpoints) for LLM integration.

Requirements:
    - 2.1: Generate relevant technical questions for specified roles
    - 2.2: Produce role-appropriate questions
    - 4.2: Analyze answers against question and role context
    - 7.6: Separate LLM integration into dedicated service layer
"""
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel, Field

from app.core.config import settings


# Configure logging
logger = logging.getLogger(__name__)


class EvaluationScores(BaseModel):
    """Structured evaluation scores for an answer."""
    correctness: float = Field(ge=0, le=10, description="Technical correctness of the answer")
    completeness: float = Field(ge=0, le=10, description="Completeness of the answer")
    quality: float = Field(ge=0, le=10, description="Code quality and best practices")
    communication: float = Field(ge=0, le=10, description="Clarity of communication")


class EvaluationResult(BaseModel):
    """Complete evaluation result with scores, feedback, and suggestions."""
    scores: EvaluationScores
    feedback: str = Field(min_length=1, description="Detailed feedback on the answer")
    suggestions: List[str] = Field(min_items=1, description="Actionable improvement suggestions")


class LLMService:
    """
    Service for interacting with LLM APIs for question generation and answer evaluation.
    
    Supports multiple LLM providers:
    - OpenAI (GPT-4, GPT-3.5)
    - Google Gemini (gemini-pro, gemini-1.5-pro)
    
    This service handles:
    - Building prompts for question generation and evaluation
    - Making async API calls to LLM providers
    - Parsing and validating LLM responses
    - Error handling for API failures, timeouts, and rate limits
    - Rate limiting to prevent 429 errors (max 2 concurrent requests for Gemini free tier)
    """
    
    def __init__(self):
        """Initialize LLM service with configuration from settings."""
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY
        self.api_url = settings.LLM_API_URL
        self.model = settings.LLM_MODEL
        
        # Rate limiter: Allow ONLY 1 concurrent API call at a time for Gemini free tier
        # This prevents 429 "Too Many Requests" errors
        self._rate_limiter = asyncio.Semaphore(1)
        
        # Validate configuration
        if not self.api_key:
            logger.warning("LLM_API_KEY not configured - LLM service will not function")
        
        if self.provider not in ["openai", "gemini"]:
            logger.warning(f"Unknown LLM provider: {self.provider}, defaulting to openai")
            self.provider = "openai"
    
    async def _call_llm_api(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: float = 30.0
    ) -> str:
        """
        Make an async API call to the LLM provider with rate limiting.
        
        Uses a semaphore to limit concurrent API calls to prevent 429 errors.
        For Gemini free tier, max 2 concurrent requests are allowed.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in the response
            timeout: Request timeout in seconds
            
        Returns:
            LLM response text
            
        Raises:
            httpx.HTTPStatusError: For API errors (4xx, 5xx)
            httpx.TimeoutException: For request timeouts
            httpx.RequestError: For network errors
            ValueError: For invalid API key or configuration
            
        Requirements:
            - 7.6: Async HTTP calls for LLM integration
        """
        if not self.api_key:
            raise ValueError("LLM_API_KEY not configured")
        
        # Use rate limiter to prevent too many concurrent requests
        async with self._rate_limiter:
            logger.info(f"Acquired rate limiter slot (provider: {self.provider})")
            
            if self.provider == "gemini":
                result = await self._call_gemini_api(prompt, temperature, max_tokens, timeout)
            else:
                result = await self._call_openai_api(prompt, temperature, max_tokens, timeout)
            
            logger.info("Released rate limiter slot")
            return result
    
    async def _call_openai_api(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        timeout: float
    ) -> str:
        """Call OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.info(f"Calling OpenAI API: {self.api_url} with model {self.model}")
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                logger.info(f"OpenAI API call successful, received {len(content)} characters")
                return content
                
        except httpx.TimeoutException as e:
            logger.error(f"OpenAI API timeout after {timeout}s: {e}")
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("OpenAI API rate limit exceeded")
            elif e.response.status_code == 401:
                logger.error("OpenAI API authentication failed - check API key")
            else:
                logger.error(f"OpenAI API error {e.response.status_code}: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse OpenAI API response: {e}")
            raise ValueError(f"Invalid OpenAI API response format: {e}")
    
    async def _call_gemini_api(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        timeout: float
    ) -> str:
        """Call Google Gemini API with retry logic for rate limits."""
        # Gemini API URL format: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}
        # Note: v1 (not v1beta) is the stable endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
                # Note: responseMimeType removed as it causes truncation issues
            }
        }
        
        # Retry logic for rate limits (disabled for testing)
        max_retries = 0  # Temporarily disabled - semaphore should prevent 429
        base_delay = 2  # seconds
        
        for attempt in range(max_retries + 1):  # +1 to ensure at least one attempt
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    logger.info(f"Calling Gemini API with model {self.model} (attempt {attempt + 1})")
                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    
                    # Parse response
                    data = response.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    logger.info(f"Gemini API call successful, received {len(content)} characters")
                    return content
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit - should not happen with semaphore, but log if it does
                    logger.error("Gemini API rate limit exceeded despite semaphore - check configuration")
                    raise
                elif e.response.status_code == 401 or e.response.status_code == 403:
                    logger.error("Gemini API authentication failed - check API key")
                    raise
                elif e.response.status_code == 404:
                    logger.error(f"Gemini API 404 - model '{self.model}' not found. Try 'gemini-1.5-flash' or 'gemini-1.5-pro'")
                    raise
                else:
                    logger.error(f"Gemini API error {e.response.status_code}: {e}")
                    raise
            except httpx.TimeoutException as e:
                logger.error(f"Gemini API timeout after {timeout}s: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Gemini API request failed: {e}")
                raise
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse Gemini API response: {e}")
                raise ValueError(f"Invalid Gemini API response format: {e}")
        
        # Should never reach here, but just in case
        raise ValueError("Failed to call Gemini API after all retries")
    
    def _build_question_prompt(self, role: str, num_questions: int) -> str:
        """
        Build a prompt for generating interview questions for a specific role.
        
        Args:
            role: The job role/position for which to generate questions
            num_questions: Number of questions to generate
            
        Returns:
            Formatted prompt string for the LLM
            
        Requirements:
            - 2.1: Generate relevant technical questions
            - 2.2: Produce role-appropriate questions
        """
        prompt = f"""Generate {num_questions} technical interview questions for a {role} position.

Requirements:
- Questions should be relevant to the {role} role
- Include a mix of theoretical and practical questions
- Questions should assess technical knowledge, problem-solving, and coding skills
- Make questions clear and specific
- Avoid yes/no questions
- Keep each question concise (under 200 characters)

Return ONLY a JSON array of {num_questions} question strings. Do not include any markdown formatting or explanations.

Example format:
["Question 1 text here", "Question 2 text here", "Question 3 text here"]

Generate exactly {num_questions} questions now."""
        
        return prompt
    
    async def generate_questions(self, role: str, num_questions: int) -> List[str]:
        """
        Generate interview questions for a specific role using the LLM.
        
        Args:
            role: The job role/position for which to generate questions
            num_questions: Number of questions to generate (1-10)
            
        Returns:
            List of generated question strings
            
        Raises:
            ValueError: If num_questions is out of range or LLM response is invalid
            httpx exceptions: For API failures
            
        Requirements:
            - 2.1: Generate relevant technical questions for specified roles
            - 2.2: Produce role-appropriate questions
        """
        if not 1 <= num_questions <= 10:
            raise ValueError("num_questions must be between 1 and 10")
        
        logger.info(f"Generating {num_questions} questions for role: {role}")
        
        # Build prompt
        prompt = self._build_question_prompt(role, num_questions)
        
        # Call LLM API
        response = await self._call_llm_api(
            prompt,
            temperature=0.8,  # More creative for question generation
            max_tokens=2000
        )
        
        # Parse response as JSON array
        try:
            # Clean response - remove markdown code blocks if present
            response_text = response.strip()
            
            # Remove ```json and ``` markers if present
            if response_text.startswith('```'):
                # Find the first newline after ```json or ```
                first_newline = response_text.find('\n')
                if first_newline != -1:
                    response_text = response_text[first_newline + 1:]
                
                # Remove trailing ```
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                response_text = response_text.strip()
            
            questions = json.loads(response_text)
            
            if not isinstance(questions, list):
                raise ValueError("LLM response is not a JSON array")
            
            if len(questions) != num_questions:
                logger.warning(
                    f"Expected {num_questions} questions but got {len(questions)}, "
                    f"adjusting..."
                )
                # Take first num_questions or pad with generic questions
                if len(questions) > num_questions:
                    questions = questions[:num_questions]
                elif len(questions) < num_questions:
                    # Pad with generic questions if needed
                    while len(questions) < num_questions:
                        questions.append(
                            f"Describe your experience with {role} responsibilities."
                        )
            
            logger.info(f"Successfully generated {len(questions)} questions")
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response[:200]}...")
            raise ValueError(f"LLM returned invalid JSON: {e}")
    
    def _build_evaluation_prompt(
        self,
        question: str,
        answer: str,
        role: str
    ) -> str:
        """
        Build a prompt for evaluating a candidate's answer to an interview question.
        
        Args:
            question: The interview question that was asked
            answer: The candidate's answer to evaluate
            role: The job role/position context
            
        Returns:
            Formatted prompt string for the LLM
            
        Requirements:
            - 4.2: Analyze answer against question and role context
        """
        prompt = f"""Evaluate this {role} candidate's answer. Return ONLY valid JSON, no markdown.

Question: {question}
Answer: {answer}

Return this exact JSON structure:
{{
  "scores": {{
    "correctness": 8.5,
    "completeness": 7.0,
    "quality": 9.0,
    "communication": 8.0
  }},
  "feedback": "Detailed feedback here",
  "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}

Scores are 0-10. Provide at least 3 suggestions. Be specific and constructive."""
        
        return prompt
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        role: str
    ) -> EvaluationResult:
        """
        Evaluate a candidate's answer using the LLM.
        
        Args:
            question: The interview question that was asked
            answer: The candidate's answer to evaluate
            role: The job role/position context
            
        Returns:
            EvaluationResult with scores, feedback, and suggestions
            
        Raises:
            ValueError: If LLM response is invalid or cannot be parsed
            httpx exceptions: For API failures
            
        Requirements:
            - 4.2: Analyze answer against question and role context
            - 5.1, 5.2, 5.3: Produce structured evaluation with scores, feedback, suggestions
        """
        logger.info(f"Evaluating answer for role: {role}")
        
        # Build prompt
        prompt = self._build_evaluation_prompt(question, answer, role)
        
        # Call LLM API with higher token limit for Gemini
        response = await self._call_llm_api(
            prompt,
            temperature=0.3,  # More deterministic for evaluation
            max_tokens=4096  # Increased for Gemini to avoid truncation
        )
        
        # Parse and validate response
        try:
            # Try to extract JSON from response (in case LLM adds extra text)
            response_text = response.strip()
            
            # Log full response for debugging
            logger.info(f"Raw LLM response: {response_text}")
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                first_newline = response_text.find('\n')
                if first_newline != -1:
                    response_text = response_text[first_newline + 1:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
            
            # Find JSON object in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error(f"No JSON found in response: {response_text}")
                raise ValueError("No JSON object found in LLM response")
            
            json_text = response_text[start_idx:end_idx]
            
            # Try to fix common JSON issues
            # Fix missing commas between properties (common Gemini issue)
            import re
            # Add comma after closing brace/bracket if followed by quote
            json_text = re.sub(r'([}\]])\s*"', r'\1,"', json_text)
            # Add comma after closing quote if followed by quote
            json_text = re.sub(r'"\s*"([a-z])', r'","\1', json_text)
            
            evaluation_data = json.loads(json_text)
            
            # Validate and parse using Pydantic
            evaluation = EvaluationResult(**evaluation_data)
            
            logger.info("Successfully evaluated answer")
            return evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM evaluation response as JSON: {e}")
            logger.error(f"Full response: {response}")
            raise ValueError(f"LLM returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to validate evaluation response: {e}")
            logger.error(f"Full response: {response}")
            raise ValueError(f"Invalid evaluation format: {e}")


# Global LLM service instance
llm_service = LLMService()
