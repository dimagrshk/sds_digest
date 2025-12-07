"""Tests for API endpoints."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import UploadFile
from io import BytesIO

from sds_digest.api.main import app, sds_storage
from sds_digest.src.processing.processor import ProcessedSafetyDataSheet, StructuredSections, StructuredSection


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear storage before each test."""
    sds_storage.clear()
    yield
    sds_storage.clear()


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "SDS Digest API", "version": "0.1.0"}


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestUploadEndpoint:
    """Tests for upload endpoint."""
    
    @patch('sds_digest.api.main.PERSISTENCE')
    @patch('sds_digest.api.main.MarkerExtractor')
    @patch('sds_digest.api.main.LLMSafetyDataSheetProcessor')
    def test_upload_success(
        self, 
        mock_processor_class, 
        mock_extractor_class, 
        mock_persistence,
        client,
        sample_processed_sds
    ):
        """Test successful SDS upload."""
        # Setup mocks
        mock_extractor = MagicMock()
        mock_extractor.extract_pdf.return_value = MagicMock(
            content="# Test SDS Content"
        )
        mock_extractor_class.return_value = mock_extractor
        
        mock_processor = AsyncMock()
        mock_processor.aprocess = AsyncMock(return_value=sample_processed_sds)
        mock_processor_class.from_openai.return_value = mock_processor
        
        mock_persistence.save_uploaded_file.return_value = "/path/to/file.pdf"
        mock_persistence.save_extracted_markdown.return_value = "/path/to/extracted.md"
        
        # Create test file
        file_content = b"PDF content"
        files = {"file": ("test_sds.pdf", BytesIO(file_content), "application/pdf")}
        
        # Make request
        response = client.post("/api/upload", files=files)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "sds_id" in data
        assert data["status"] == "success"
        assert "test_sds.pdf" in data["message"]
        
        # Verify storage
        assert data["sds_id"] in sds_storage
        assert sds_storage[data["sds_id"]] == sample_processed_sds
    
    @patch('sds_digest.api.main.PERSISTENCE')
    @patch('sds_digest.api.main.MarkerExtractor')
    def test_upload_extraction_error(self, mock_extractor_class, mock_persistence, client):
        """Test upload with extraction error."""
        # Setup mocks to raise error
        mock_extractor = MagicMock()
        mock_extractor.extract_pdf.side_effect = Exception("Extraction failed")
        mock_extractor_class.return_value = mock_extractor
        
        mock_persistence.save_uploaded_file.return_value = "/path/to/file.pdf"
        
        # Create test file
        file_content = b"PDF content"
        files = {"file": ("test_sds.pdf", BytesIO(file_content), "application/pdf")}
        
        # Make request
        response = client.post("/api/upload", files=files)
        
        # Assertions
        assert response.status_code == 500
        assert "Error processing SDS" in response.json()["detail"]


class TestStructuredExtractEndpoint:
    """Tests for structured extract endpoint."""
    
    def test_get_structured_extract_success(self, client, sample_processed_sds):
        """Test successful retrieval of structured extract."""
        # Add to storage
        sds_id = "test-sds-id"
        sds_storage[sds_id] = sample_processed_sds
        
        # Make request
        response = client.get(f"/api/sds/{sds_id}/structured")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["sds_id"] == sds_id
        assert "structured_content" in data
        assert "sections" in data
    
    def test_get_structured_extract_not_found(self, client):
        """Test retrieval of non-existent SDS."""
        response = client.get("/api/sds/non-existent-id/structured")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSummaryEndpoint:
    """Tests for summary endpoint."""
    
    def test_get_summary_success(self, client, sample_processed_sds):
        """Test successful retrieval of summary."""
        # Add to storage
        sds_id = "test-sds-id"
        sds_storage[sds_id] = sample_processed_sds
        
        # Make request
        response = client.get(f"/api/sds/{sds_id}/summary")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["sds_id"] == sds_id
        assert data["summary"] == sample_processed_sds.summary
    
    def test_get_summary_not_found(self, client):
        """Test retrieval of summary for non-existent SDS."""
        response = client.get("/api/sds/non-existent-id/summary")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestAskEndpoint:
    """Tests for ask question endpoint."""
    
    @patch('sds_digest.api.main.QALLM')
    def test_ask_question_success(self, mock_qa_llm_class, client, sample_processed_sds):
        """Test successful question answering."""
        # Setup mocks
        mock_qa_llm = AsyncMock()
        mock_qa_llm.aanswer = AsyncMock(return_value="This is a test answer.")
        mock_qa_llm_class.from_openai.return_value = mock_qa_llm
        
        # Add to storage
        sds_id = "test-sds-id"
        sds_storage[sds_id] = sample_processed_sds
        
        # Make request
        response = client.post(
            f"/api/sds/{sds_id}/ask",
            json={"question": "What is the chemical name?"}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["sds_id"] == sds_id
        assert data["question"] == "What is the chemical name?"
        assert data["answer"] == "This is a test answer."
        
        # Verify LLM was called
        mock_qa_llm.aanswer.assert_called_once()
    
    def test_ask_question_not_found(self, client):
        """Test asking question for non-existent SDS."""
        response = client.post(
            "/api/sds/non-existent-id/ask",
            json={"question": "What is the chemical name?"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_ask_question_invalid_request(self, client, sample_processed_sds):
        """Test asking question with invalid request body."""
        sds_id = "test-sds-id"
        sds_storage[sds_id] = sample_processed_sds
        
        response = client.post(
            f"/api/sds/{sds_id}/ask",
            json={}
        )
        
        assert response.status_code == 422  # Validation error

