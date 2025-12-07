"""Tests for API models."""
import pytest
from pydantic import ValidationError

from sds_digest.api.models import (
    UploadResponse,
    StructuredExtractResponse,
    SummaryResponse,
    QuestionRequest,
    QuestionResponse,
)


class TestUploadResponse:
    """Tests for UploadResponse model."""
    
    def test_upload_response_creation(self):
        """Test creating an UploadResponse."""
        response = UploadResponse(
            sds_id="test-id-123",
            message="File uploaded successfully",
            status="success"
        )
        
        assert response.sds_id == "test-id-123"
        assert response.message == "File uploaded successfully"
        assert response.status == "success"
    
    def test_upload_response_validation(self):
        """Test UploadResponse validation."""
        # Missing required fields should raise validation error
        with pytest.raises(ValidationError):
            UploadResponse(sds_id="test-id")
        
        with pytest.raises(ValidationError):
            UploadResponse(message="Test message")


class TestStructuredExtractResponse:
    """Tests for StructuredExtractResponse model."""
    
    def test_structured_extract_response_creation(self):
        """Test creating a StructuredExtractResponse."""
        response = StructuredExtractResponse(
            sds_id="test-id-123",
            structured_content={"section1": {"key": "value"}},
            sections=[{"title": "Section 1"}]
        )
        
        assert response.sds_id == "test-id-123"
        assert response.structured_content == {"section1": {"key": "value"}}
        assert len(response.sections) == 1
    
    def test_structured_extract_response_default_sections(self):
        """Test StructuredExtractResponse with default empty sections."""
        response = StructuredExtractResponse(
            sds_id="test-id-123",
            structured_content={}
        )
        
        assert response.sections == []
    
    def test_structured_extract_response_validation(self):
        """Test StructuredExtractResponse validation."""
        with pytest.raises(ValidationError):
            StructuredExtractResponse(structured_content={})


class TestSummaryResponse:
    """Tests for SummaryResponse model."""
    
    def test_summary_response_creation(self):
        """Test creating a SummaryResponse."""
        response = SummaryResponse(
            sds_id="test-id-123",
            summary="This is a test chemical summary."
        )
        
        assert response.sds_id == "test-id-123"
        assert response.summary == "This is a test chemical summary."
    
    def test_summary_response_validation(self):
        """Test SummaryResponse validation."""
        with pytest.raises(ValidationError):
            SummaryResponse(sds_id="test-id")
        
        with pytest.raises(ValidationError):
            SummaryResponse(summary="Test summary")


class TestQuestionRequest:
    """Tests for QuestionRequest model."""
    
    def test_question_request_creation(self):
        """Test creating a QuestionRequest."""
        request = QuestionRequest(
            question="What is the chemical name?"
        )
        
        assert request.question == "What is the chemical name?"
    
    def test_question_request_validation(self):
        """Test QuestionRequest validation."""
        with pytest.raises(ValidationError):
            QuestionRequest()
        
        # Empty string should be valid (validation might allow it)
        request = QuestionRequest(question="")
        assert request.question == ""


class TestQuestionResponse:
    """Tests for QuestionResponse model."""
    
    def test_question_response_creation(self):
        """Test creating a QuestionResponse."""
        response = QuestionResponse(
            sds_id="test-id-123",
            question="What is the chemical name?",
            answer="The chemical name is Test Chemical."
        )
        
        assert response.sds_id == "test-id-123"
        assert response.question == "What is the chemical name?"
        assert response.answer == "The chemical name is Test Chemical."
    
    def test_question_response_validation(self):
        """Test QuestionResponse validation."""
        with pytest.raises(ValidationError):
            QuestionResponse(
                sds_id="test-id",
                question="Test question"
            )
