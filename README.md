# SDS Digest

A system for processing Safety Data Sheets (SDS) using Large Language Models (LLMs) to extract structured information, generate summaries, and answer questions about chemical safety data.

## Overview

SDS Digest processes PDF Safety Data Sheets by converting them to markdown format and then using LLMs to extract structured information, generate summaries, and enable question-answering capabilities. The system supports both OpenAI and Ollama LLM backends.

## Motivation

### Full Document Context Instead of RAG

Rather than using Retrieval-Augmented Generation (RAG) with chunking and vector databases, this system uses the full document as context. Safety Data Sheets typically contain approximately 5000 tokens when converted to markdown, which fits comfortably within modern LLM context windows. This approach simplifies the architecture by avoiding the complexity of chunking, embedding, and retrieval while still providing complete context for accurate information extraction and question answering.

### LLM-Based Section Structuring

Standard approaches to extract structured information from SDS sections (such as regex patterns, rule-based parsers, or template matching) were insufficient due to the variability in section formatting across different SDS documents. Each section is therefore processed individually with an LLM, which can adapt to different document structures and extract information reliably regardless of formatting variations.

## Approach

### Processing Pipeline

The system follows a multi-stage processing pipeline:

1. **PDF to Markdown Conversion**: PDF files are converted to markdown format using the `MarkerExtractor` (powered by the `marker-pdf` library). This preserves the document structure and makes the content accessible for LLM processing.

2. **Section Extraction**: The markdown content is analyzed by `SDSStructureLLM` to identify and extract individual sections from the SDS document. This creates a structured list of sections with titles, summaries, and raw content.

3. **Section Structuring**: Each extracted section is processed by `SectionStructureLLM` to convert the raw section content into structured JSON format. This enables programmatic access to specific information within each section.

4. **Summary Generation**: The entire markdown content is processed by `SummaryLLM` to generate a concise summary of the chemical substance described in the SDS.

5. **Question Answering**: Users can query the processed SDS using `QALLM`, which uses the markdown content as context to answer questions about the safety data.

6. **Answer Judging** (for benchmarking): The `JudgeLLM` evaluates answer quality against acceptance criteria, useful for benchmarking and quality assurance.

### LLM Processing Architecture

The processing is orchestrated by `LLMSafetyDataSheetProcessor` (`sds_digest/src/processing/llm_processor.py`), which coordinates the different LLM components:

- **Synchronous Processing** (`process` method): Processes sections sequentially and generates a summary.
- **Asynchronous Processing** (`aprocess` method): 
  - Extracts sections asynchronously
  - Processes sections in parallel with a semaphore (max 5 concurrent requests) for controlled concurrency
  - Generates summary concurrently with section processing for improved performance

The processor supports both OpenAI and Ollama backends, allowing flexibility in LLM provider selection.

### LLM Components

Located in `sds_digest/llms/`:

- **`structure_llm.py`**: Contains `SDSStructureLLM` (extracts sections) and `SectionStructureLLM` (structures individual sections)
- **`summary_llm.py`**: Contains `SummaryLLM` for generating concise summaries
- **`qa_llm.py`**: Contains `QALLM` for answering questions about the SDS
- **`judge_llm.py`**: Contains `JudgeLLM` for evaluating answer quality

All LLM components use structured prompts from `sds_digest/llms/prompts/` and support both OpenAI and Ollama providers.

## Installation

Install dependencies using Poetry:

```bash
poetry install
```

## Running the Application

### Using Make Commands

```bash
# Install dependencies
make install

# Run the FastAPI backend
make api

# Run the Streamlit frontend
make frontend

# Run both API and frontend concurrently
make run
```

### Manual Execution

#### FastAPI Backend

The FastAPI backend provides REST API endpoints for processing SDS documents.

Start the API server:

```bash
poetry run python sds_digest/run_api.py
```

Or using uvicorn directly:

```bash
poetry run uvicorn sds_digest.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**API Documentation**:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

**Available Endpoints**:
- `POST /api/upload` - Upload and process a SDS PDF
- `GET /api/sds/{sds_id}/structured` - Get structured JSON extract
- `GET /api/sds/{sds_id}/summary` - Get concise summary
- `POST /api/sds/{sds_id}/ask` - Ask questions about the SDS


#### Streamlit Frontend

The Streamlit frontend provides a user-friendly interface for interacting with the SDS processing system.

Start the frontend:

```bash
poetry run python sds_digest/run_frontend.py
```

Or using streamlit directly:

```bash
poetry run streamlit run sds_digest/frontend/app.py --server.port 8501
```

The frontend will be available at `http://localhost:8501`

**Features**:
- **Upload SDS**: Upload and process PDF files
- **View Structured Extract**: View the structured JSON representation
- **View Summary**: View a concise summary of the chemical
- **Ask Questions**: Interactive Q&A interface for querying SDS details

## Testing

The project includes comprehensive tests using pytest. Tests are located in the `tests/` directory.

### Running Tests

Run all tests:

```bash
poetry run pytest
```

Run tests with verbose output:

```bash
poetry run pytest -v
```

Run specific test files:

```bash
# Test API endpoints
poetry run pytest tests/test_api.py

# Test models
poetry run pytest tests/test_models.py
```

### Test Structure

- **`tests/test_api.py`**: Tests for FastAPI endpoints including:
  - Root and health check endpoints
  - Upload endpoint with success and error cases
  - Structured extract retrieval
  - Summary retrieval
  - Question answering functionality

Tests use mocking to avoid requiring actual LLM API calls or file system operations during testing.

## Configuration

The system requires API keys for OpenAI (if using OpenAI models). Configure these in `sds_digest/src/secrets.py` or through environment variables.

## Project Structure

```
sds_digest/
├── api/              # FastAPI application and endpoints
├── frontend/         # Streamlit frontend application
├── llms/             # LLM components (structure, summary, QA, judge)
│   └── prompts/      # LLM prompt templates
├── src/
│   ├── extraction/   # PDF extraction (MarkerExtractor)
│   └── processing/   # Processing pipeline (LLMSafetyDataSheetProcessor)
└── tests/            # Test suite
```

## Possible Future Improvements

- Adjust parsing with alternative methods (Unstruct, VLM, Marker)
- Better benchmarking with deepeval or ragas
- Extraction improvements (RAG, Hierarchical generation)
- Implement chunking and indexing for large documents
- Add vector database support once needed (FAISS or Chroma)
