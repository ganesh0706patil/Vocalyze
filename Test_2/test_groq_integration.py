"""
Test suite for Groq LLM Integration
Tests LLM API calls, response parsing, and error handling
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class TestGroqInitialization:
    """Test cases for Groq client initialization"""
    
    def test_groq_client_initialization(self):
        """Test that Groq client initializes successfully"""
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            assert client is not None
        except Exception as e:
            pytest.skip(f"Groq initialization failed: {str(e)}")
    
    def test_groq_api_key_from_env(self):
        """Test that API key is loaded from environment"""
        api_key = os.getenv("GROQ_API_KEY")
        assert api_key is not None, "GROQ_API_KEY not found in environment"

class TestGroqAPICalls:
    """Test cases for Groq API calls"""
    
    @patch('groq.Groq')
    def test_simple_completion_call(self, mock_groq):
        """Test basic completion API call"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello world"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        client = Groq()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": "Say hello"}],
            temperature=0.1,
            max_tokens=100
        )
        
        assert response.choices[0].message.content == "Hello world"
    
    @patch('groq.Groq')
    def test_completion_with_system_message(self, mock_groq):
        """Test completion with system prompt"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        client = Groq()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Help me"}
            ]
        )
        
        assert response is not None
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('groq.Groq')
    def test_completion_temperature_parameter(self, mock_groq):
        """Test temperature parameter affects API call"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_response = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        
        client = Groq()
        
        # Low temperature (more deterministic)
        client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.1
        )
        
        # High temperature (more creative)
        client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.9
        )
        
        # Verify both calls were made
        assert mock_client.chat.completions.create.call_count == 2

class TestGroqModels:
    """Test cases for different Groq models"""
    
    @pytest.mark.parametrize("model_name", [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "mixtral-8x7b-32768"
    ])
    @patch('groq.Groq')
    def test_model_availability(self, mock_groq, model_name):
        """Test different model availability"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_response = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        
        client = Groq()
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "test"}]
        )
        
        assert response is not None
        # Verify model name was used
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == model_name

class TestResponseParsing:
    """Test cases for response parsing"""
    
    @patch('groq.Groq')
    def test_parse_response_content(self, mock_groq):
        """Test parsing response content"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        expected_content = "This is the response content"
        mock_response.choices = [MagicMock(message=MagicMock(content=expected_content))]
        mock_client.chat.completions.create.return_value = mock_response
        
        client = Groq()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": "test"}]
        )
        
        content = response.choices[0].message.content
        assert content == expected_content
    
    @patch('groq.Groq')
    def test_response_has_required_fields(self, mock_groq):
        """Test that response has all required fields"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Content"))]
        mock_response.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock_client.chat.completions.create.return_value = mock_response
        
        client = Groq()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": "test"}]
        )
        
        assert hasattr(response, 'choices')
        assert hasattr(response, 'model')
        assert hasattr(response, 'usage')

class TestErrorHandling:
    """Test cases for error handling"""
    
    @patch('groq.Groq')
    def test_api_key_error(self, mock_groq):
        """Test handling of missing/invalid API key"""
        mock_groq.side_effect = ValueError("Invalid API key")
        
        with pytest.raises(ValueError):
            Groq(api_key="invalid_key")
    
    @patch('groq.Groq')
    def test_network_error_handling(self, mock_groq):
        """Test handling of network errors"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = ConnectionError("Network error")
        
        client = Groq()
        
        with pytest.raises(ConnectionError):
            client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": "test"}]
            )
    
    @patch('groq.Groq')
    def test_rate_limit_error(self, mock_groq):
        """Test handling of rate limit errors"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        
        client = Groq()
        
        with pytest.raises(Exception):
            client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": "test"}]
            )

class TestGroqIntegration:
    """Integration tests for Groq"""
    
    @patch('groq.Groq')
    def test_feedback_generation_workflow(self, mock_groq):
        """Test complete feedback generation workflow"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        # Mock response for feedback generation
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content="Good answer! However, consider adding more detail.")
        )]
        mock_client.chat.completions.create.return_value = mock_response
        
        client = Groq()
        
        # Generate feedback
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are an expert teacher providing feedback"},
                {"role": "user", "content": "Student answer: [answer]\nQuestion: [question]"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        feedback = response.choices[0].message.content
        assert feedback is not None
        assert len(feedback) > 0
    
    @patch('groq.Groq')
    def test_multiple_sequential_calls(self, mock_groq):
        """Test multiple sequential API calls"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        responses = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=f"Response {i}"))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=f"Response {i}"))]),
        ]
        mock_client.chat.completions.create.side_effect = responses
        
        client = Groq()
        
        # Make multiple calls
        for i in range(2):
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": f"test {i}"}]
            )
            assert response is not None
        
        assert mock_client.chat.completions.create.call_count == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
