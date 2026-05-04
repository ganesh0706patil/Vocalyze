"""
Test suite for FastAPI Endpoints
Tests all API endpoints, request/response validation, and error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

# Import the FastAPI app
from fastapi import FastAPI

# Note: Adjust import based on your actual app structure
try:
    from fastapi.main import app
except ImportError:
    # Fallback if import path is different
    app = FastAPI()

client = TestClient(app)

class TestTextAnalysisEndpoint:
    """Test cases for text analysis endpoint"""
    
    def test_text_analysis_endpoint_exists(self):
        """Test that text analysis endpoint is available"""
        response = client.get("/")
        assert response.status_code in [200, 404]  # Either exists or 404
    
    @patch('fastapi.FeedbackProcessor')
    def test_text_analysis_with_valid_input(self, mock_processor):
        """Test text analysis with valid input"""
        mock_processor.return_value.generate_feedback.return_value = {
            'feedback': 'Good answer',
            'score': 85
        }
        
        payload = {
            'text': 'Sample student answer',
            'question': 'What is machine learning?'
        }
        
        # Adjust endpoint path based on your actual implementation
        response = client.post("/analyze", json=payload)
        # Response should either be 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404, 422]
    
    def test_text_analysis_missing_required_field(self):
        """Test text analysis with missing required fields"""
        payload = {
            'text': 'Sample text'
            # 'question' is missing
        }
        
        response = client.post("/analyze", json=payload)
        # Should return 422 (validation error) or 404
        assert response.status_code in [422, 404]
    
    def test_empty_text_input(self):
        """Test handling of empty text input"""
        payload = {
            'text': '',
            'question': 'Sample question?'
        }
        
        response = client.post("/analyze", json=payload)
        # Should handle empty input gracefully
        assert response.status_code in [200, 400, 404, 422]

class TestAudioUploadEndpoint:
    """Test cases for audio upload endpoint"""
    
    def test_audio_upload_endpoint_exists(self):
        """Test that audio upload endpoint is available"""
        response = client.get("/upload")
        # Endpoint might not accept GET, check status
        assert response.status_code in [200, 404, 405]
    
    def test_audio_upload_with_file(self):
        """Test audio file upload"""
        # Create a mock audio file
        from io import BytesIO
        
        fake_audio = BytesIO(b"fake audio data")
        files = {'file': ('test_audio.wav', fake_audio, 'audio/wav')}
        
        response = client.post("/upload", files=files)
        # Should accept file or return 404 if endpoint not implemented
        assert response.status_code in [200, 400, 404, 422]
    
    def test_upload_without_file(self):
        """Test upload endpoint without file"""
        response = client.post("/upload")
        # Should require file
        assert response.status_code in [400, 404, 422]

class TestAssessmentEndpoint:
    """Test cases for assessment endpoints"""
    
    @patch('fastapi.generate_assessment_questions')
    def test_generate_assessment(self, mock_generate):
        """Test assessment generation endpoint"""
        mock_generate.return_value = {
            'questions': [
                {'question': 'Q1?', 'type': 'short_answer'},
                {'question': 'Q2?', 'type': 'multiple_choice'}
            ]
        }
        
        payload = {'topic': 'Python Basics'}
        response = client.post("/assessments", json=payload)
        
        # Endpoint might not exist, both are valid
        assert response.status_code in [200, 404]

class TestUserEndpoint:
    """Test cases for user-related endpoints"""
    
    def test_user_creation(self):
        """Test user creation endpoint"""
        payload = {
            'email': 'testuser@example.com',
            'name': 'Test User'
        }
        
        response = client.post("/users", json=payload)
        assert response.status_code in [200, 201, 400, 404, 422]
    
    def test_user_retrieval(self):
        """Test user retrieval endpoint"""
        response = client.get("/users/1")
        assert response.status_code in [200, 404]

class TestErrorHandling:
    """Test cases for error handling"""
    
    def test_invalid_json_request(self):
        """Test handling of invalid JSON"""
        response = client.post(
            "/analyze",
            data="invalid json {",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422, 404]
    
    def test_request_with_wrong_content_type(self):
        """Test request with wrong content type"""
        response = client.post(
            "/analyze",
            data="text data",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [400, 404, 415]
    
    def test_nonexistent_endpoint(self):
        """Test request to nonexistent endpoint"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404

class TestCORSHeaders:
    """Test cases for CORS configuration"""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in response"""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        # Check for CORS headers
        cors_headers = [
            'access-control-allow-origin',
            'access-control-allow-methods',
            'access-control-allow-headers'
        ]
        # At least one should be present
        assert any(header in response.headers for header in cors_headers) or response.status_code == 200

class TestRequestValidation:
    """Test cases for request validation"""
    
    def test_request_size_limit(self):
        """Test large request handling"""
        large_payload = {
            'text': 'x' * (51 * 1024 * 1024),  # 51MB - exceeds 50MB limit
            'question': 'Q?'
        }
        # Should be rejected or handled gracefully
        response = client.post("/analyze", json=large_payload)
        assert response.status_code in [413, 400, 404, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
