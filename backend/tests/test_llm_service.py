"""
Unit tests for LLM service.
Tests prompt building, API interaction, and response parsing.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.llm_service import (
    LLMService,
    EvaluationResult,
    EvaluationScores
)


@pytest.fixture
def llm_service():
    """Create LLM service instance for testing."""
    service = LLMService()
    service.api_key = "test-api-key"
    service.api_url = "https://api.test.com/v1/chat/completions"
    service.model = "gpt-4"
    return service


class TestPromptBuilding:
    """Test prompt building functions."""
    
    def test_build_question_prompt(self, llm_service):
        """Test question generation prompt building."""
        prompt = llm_service._build_question_prompt("Python Developer", 3)
        
        assert "Python Developer" in prompt
        assert "3" in prompt
        assert "technical interview questions" in prompt.lower()
        assert "JSON array" in prompt
    
    def test_build_evaluation_prompt(self, llm_service):
        """Test evaluation prompt building."""
        question = "What is a closure in Python?"
        answer = "A closure is a function that captures variables from its enclosing scope."
        role = "Python Developer"
        
        prompt = llm_service._build_evaluation_prompt(question, answer, role)
        
        assert question in prompt
        assert answer in prompt
        assert role in prompt
        assert "correctness" in prompt.lower()
        assert "feedback" in prompt.lower()
        assert "suggestions" in prompt.lower()


class TestQuestionGeneration:
    """Test question generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_questions_success(self, llm_service):
        """Test successful question generation."""
        mock_response = json.dumps([
            "What is your experience with Python?",
            "Explain the difference between list and tuple.",
            "How do you handle exceptions in Python?"
        ])
        
        with patch.object(llm_service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            questions = await llm_service.generate_questions("Python Developer", 3)
            
            assert len(questions) == 3
            assert all(isinstance(q, str) for q in questions)
            assert all(len(q) > 0 for q in questions)
            mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_questions_invalid_count(self, llm_service):
        """Test question generation with invalid count."""
        with pytest.raises(ValueError, match="must be between 1 and 10"):
            await llm_service.generate_questions("Python Developer", 0)
        
        with pytest.raises(ValueError, match="must be between 1 and 10"):
            await llm_service.generate_questions("Python Developer", 11)
    
    @pytest.mark.asyncio
    async def test_generate_questions_invalid_json(self, llm_service):
        """Test handling of invalid JSON response."""
        with patch.object(llm_service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "This is not valid JSON"
            
            with pytest.raises(ValueError, match="invalid JSON"):
                await llm_service.generate_questions("Python Developer", 3)
    
    @pytest.mark.asyncio
    async def test_generate_questions_wrong_count(self, llm_service):
        """Test handling when LLM returns wrong number of questions."""
        # LLM returns 5 questions but we asked for 3
        mock_response = json.dumps([
            "Question 1", "Question 2", "Question 3", "Question 4", "Question 5"
        ])
        
        with patch.object(llm_service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            questions = await llm_service.generate_questions("Python Developer", 3)
            
            # Should truncate to requested count
            assert len(questions) == 3


class TestAnswerEvaluation:
    """Test answer evaluation functionality."""
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_success(self, llm_service):
        """Test successful answer evaluation."""
        mock_response = json.dumps({
            "scores": {
                "correctness": 8.5,
                "completeness": 7.0,
                "quality": 8.0,
                "communication": 9.0
            },
            "feedback": "Good answer with clear explanation.",
            "suggestions": [
                "Add more examples",
                "Discuss edge cases",
                "Mention performance considerations"
            ]
        })
        
        with patch.object(llm_service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            result = await llm_service.evaluate_answer(
                question="What is a closure?",
                answer="A closure captures variables from outer scope.",
                role="Python Developer"
            )
            
            assert isinstance(result, EvaluationResult)
            assert result.scores.correctness == 8.5
            assert result.scores.completeness == 7.0
            assert result.scores.quality == 8.0
            assert result.scores.communication == 9.0
            assert len(result.feedback) > 0
            assert len(result.suggestions) == 3
            mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_with_extra_text(self, llm_service):
        """Test evaluation when LLM adds extra text around JSON."""
        mock_response = """Here's my evaluation:
        
        {
            "scores": {
                "correctness": 8.0,
                "completeness": 7.5,
                "quality": 8.5,
                "communication": 9.0
            },
            "feedback": "Well structured answer.",
            "suggestions": ["Add examples", "Discuss alternatives", "Mention best practices"]
        }
        
        Hope this helps!"""
        
        with patch.object(llm_service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            result = await llm_service.evaluate_answer(
                question="What is a closure?",
                answer="A closure captures variables.",
                role="Python Developer"
            )
            
            assert isinstance(result, EvaluationResult)
            assert result.scores.correctness == 8.0
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_invalid_json(self, llm_service):
        """Test handling of invalid JSON in evaluation response."""
        with patch.object(llm_service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "This is not valid JSON"
            
            with pytest.raises(ValueError, match="No JSON object found"):
                await llm_service.evaluate_answer(
                    question="What is a closure?",
                    answer="A closure captures variables.",
                    role="Python Developer"
                )
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_invalid_structure(self, llm_service):
        """Test handling of invalid evaluation structure."""
        mock_response = json.dumps({
            "scores": {
                "correctness": 15.0,  # Invalid: > 10
                "completeness": 7.0
            },
            "feedback": "Good answer"
            # Missing suggestions
        })
        
        with patch.object(llm_service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            with pytest.raises(ValueError, match="Invalid evaluation format"):
                await llm_service.evaluate_answer(
                    question="What is a closure?",
                    answer="A closure captures variables.",
                    role="Python Developer"
                )


class TestAPIInteraction:
    """Test LLM API interaction."""
    
    @pytest.mark.asyncio
    async def test_call_llm_api_success(self, llm_service):
        """Test successful API call."""
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": "Test response from LLM"
                    }
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client_class.return_value = mock_client
            
            result = await llm_service._call_llm_api("Test prompt")
            
            assert result == "Test response from LLM"
            mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_llm_api_no_api_key(self, llm_service):
        """Test API call without API key."""
        llm_service.api_key = ""
        
        with pytest.raises(ValueError, match="LLM_API_KEY not configured"):
            await llm_service._call_llm_api("Test prompt")
    
    @pytest.mark.asyncio
    async def test_call_llm_api_timeout(self, llm_service):
        """Test API call timeout handling."""
        async def mock_post(*args, **kwargs):
            raise httpx.TimeoutException("Request timeout")
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = mock_post
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            with pytest.raises(httpx.TimeoutException):
                await llm_service._call_llm_api("Test prompt", timeout=1.0)
    
    @pytest.mark.asyncio
    async def test_call_llm_api_rate_limit(self, llm_service):
        """Test API rate limit handling."""
        async def mock_post(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 429
            raise httpx.HTTPStatusError(
                "Rate limit exceeded",
                request=MagicMock(),
                response=mock_response
            )
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = mock_post
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await llm_service._call_llm_api("Test prompt")
    
    @pytest.mark.asyncio
    async def test_call_llm_api_auth_error(self, llm_service):
        """Test API authentication error handling."""
        async def mock_post(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 401
            raise httpx.HTTPStatusError(
                "Unauthorized",
                request=MagicMock(),
                response=mock_response
            )
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = mock_post
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await llm_service._call_llm_api("Test prompt")
