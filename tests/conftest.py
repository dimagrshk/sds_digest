"""Pytest configuration and shared fixtures."""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient

from sds_digest.api.main import app
from sds_digest.src.extraction.extractor import ExtractedPdf
from sds_digest.src.processing.processor import (
    ProcessedSafetyDataSheet,
    StructuredSections,
    StructuredSection,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a sample PDF file path (mock)."""
    pdf_path = temp_dir / "sample.pdf"
    pdf_path.touch()
    return str(pdf_path)


@pytest.fixture
def sample_extracted_pdf():
    """Create a sample ExtractedPdf object."""
    return ExtractedPdf(
        content="# Safety Data Sheet\n\n## Section 1: Identification\nChemical name: Test Chemical",
        source_file_path="/path/to/sample.pdf"
    )


@pytest.fixture
def sample_structured_sections():
    """Create sample structured sections."""
    return StructuredSections(
        structured_sections=[
            StructuredSection(
                section_title="Identification",
                section_summary="Test chemical identification",
                structured_content={"chemical_name": "Test Chemical", "cas_number": "123-45-6"}
            )
        ]
    )


@pytest.fixture
def sample_processed_sds(sample_extracted_pdf, sample_structured_sections):
    """Create a sample ProcessedSafetyDataSheet."""
    return ProcessedSafetyDataSheet(
        markdown_content=sample_extracted_pdf.content,
        structured_content=sample_structured_sections,
        summary="This is a test chemical used for testing purposes."
    )


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
