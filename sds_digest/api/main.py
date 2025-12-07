from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Dict

from sds_digest.api.models import (
    UploadResponse,
    StructuredExtractResponse,
    SummaryResponse,
    QuestionRequest,
    QuestionResponse,
)
from sds_digest.api.persistence import PERSISTENCE
from sds_digest.llms.qa_llm import QALLM
from sds_digest.src.extraction.marker_extractor import MarkerExtractor
from sds_digest.src.processing.llm_processor import LLMSafetyDataSheetProcessor
from sds_digest.src.processing.processor import ProcessedSafetyDataSheet



app = FastAPI(
    title="SDS Digest API",
    description="API for processing Safety Data Sheets (SDS)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sds_storage: Dict[str, ProcessedSafetyDataSheet] = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SDS Digest API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_sds(file: UploadFile = File(...)):
    """
    Upload and process a Safety Data Sheet PDF.
    
    This endpoint accepts a PDF file, extracts text, and processes it.
    Returns a unique SDS ID for subsequent operations.
    """
    sds_id = str(uuid.uuid4())
    try:
        # 1. Save uploaded file
        pdf_path = PERSISTENCE.save_uploaded_file(sds_id, file)
        # 2. Extract text using MarkerExtractor or similar
        extractor = MarkerExtractor()
        extracted_pdf = extractor.extract_pdf(str(pdf_path))
        _ = PERSISTENCE.save_extracted_markdown(sds_id, extracted_pdf.content)
        # 3. Process with StructureSDSLLM to get sections
        processor = LLMSafetyDataSheetProcessor.from_openai()
        processed_sds = await processor.aprocess(extracted_pdf)
        # 4. Store in database/storage
        sds_storage[sds_id] = processed_sds
        
        return UploadResponse(
            sds_id=sds_id,
            message=f"SDS uploaded and processed successfully: {file.filename}",
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing SDS: {str(e)}")


@app.get("/api/sds/{sds_id}/structured", response_model=StructuredExtractResponse)
async def get_structured_extract(sds_id: str):
    """
    Get the structured JSON extract of a processed SDS.
    
    Returns the structured representation with sections and extracted fields.
    """
    if sds_id not in sds_storage:
        raise HTTPException(status_code=404, detail=f"SDS with ID {sds_id} not found")

    processed_sds = sds_storage[sds_id]
    structured_content = processed_sds.structured_content.model_dump()
    
    
    return StructuredExtractResponse(
        sds_id=sds_id,
        structured_content=structured_content,
        sections=[]
    )


@app.get("/api/sds/{sds_id}/summary", response_model=SummaryResponse)
async def get_summary(sds_id: str):
    """
    Get a concise summary of the chemical described in the SDS.
    
    Returns a short summary generated using LLM.
    """
    if sds_id not in sds_storage:
        raise HTTPException(status_code=404, detail=f"SDS with ID {sds_id} not found")

    processed_sds = sds_storage[sds_id]
    summary = processed_sds.summary
    
    return SummaryResponse(
        sds_id=sds_id,
        summary=summary
    )


@app.post("/api/sds/{sds_id}/ask", response_model=QuestionResponse)
async def ask_question(sds_id: str, request: QuestionRequest):
    """
    Ask a question about the chemical details in the SDS.
    
    Uses LLM to answer questions based on the SDS content.
    """
    if sds_id not in sds_storage:
        raise HTTPException(status_code=404, detail=f"SDS with ID {sds_id} not found")

    qa_llm = QALLM.from_openai()
    processed_sds = sds_storage[sds_id]
    answer = await qa_llm.aanswer(request.question, processed_sds.markdown_content)
    
    return QuestionResponse(
        sds_id=sds_id,
        question=request.question,
        answer=answer,
    )
