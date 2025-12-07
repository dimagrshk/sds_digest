from pydantic import BaseModel, Field
from typing import Any, Optional


class UploadResponse(BaseModel):
    sds_id: str = Field(..., description="Unique identifier for the uploaded SDS")
    message: str = Field(..., description="Status message")
    status: str = Field(..., description="Upload status")


class StructuredExtractResponse(BaseModel):
    sds_id: str = Field(..., description="SDS identifier")
    structured_content: dict[str, Any] = Field(..., description="Structured JSON extract of the SDS")
    sections: list[dict[str, Any]] = Field(default_factory=list, description="List of sections")


class SummaryResponse(BaseModel):
    sds_id: str = Field(..., description="SDS identifier")
    summary: str = Field(..., description="Concise summary of the chemical")


class QuestionRequest(BaseModel):
    question: str = Field(..., description="Question about the SDS")


class QuestionResponse(BaseModel):
    sds_id: str = Field(..., description="SDS identifier")
    question: str = Field(..., description="The asked question")
    answer: str = Field(..., description="Answer to the question")
