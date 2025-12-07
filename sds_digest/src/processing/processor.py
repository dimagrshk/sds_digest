from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field

from sds_digest.src.extraction.extractor import ExtractedPdf



class Section(BaseModel):
    section_title: str = Field(..., description="Title of the section")
    section_summary: str = Field(..., description="Short summary")
    raw_content_of_section: str = Field(..., description="Raw content of the section")


class Sections(BaseModel):
    sections: list[Section] = Field(..., description="List of sections in structured format")


class StructuredSection(BaseModel):
    section_title: str = Field(..., description="Title of the section")
    section_summary: str = Field(..., description="Short summary")
    structured_content: dict[str, Any] = Field(..., description="Structured content of the section")


class StructuredSections(BaseModel):
    structured_sections: list[StructuredSection] = Field(..., description="List of sections in structured format")


class ProcessorIdentifier(BaseModel):
    processor_name: str
    processor_version: str


class ProcessedSafetyDataSheet(BaseModel):
    markdown_content: str = Field(..., description="The markdown content of the Safety Data Sheet")
    structured_content: StructuredSections = Field(..., description="The structured content of the Safety Data Sheet")
    summary: str = Field(..., description="The summary of the Safety Data Sheet in markdown format")
        

class SafetyDataSheetProcessor(ABC):
    processor_identifier: ProcessorIdentifier

    @abstractmethod
    def process(self, extracted_pdf: ExtractedPdf) -> ProcessedSafetyDataSheet:
        pass
