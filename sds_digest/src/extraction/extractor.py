from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class ExtractedPdf(BaseModel):
    content: str = Field(..., description="The content of the extracted PDF")
    source_file_path: str = Field(..., description="The path to the source file")


class Extractor(ABC):
    @abstractmethod
    def extract_pdf(self, pdf_path: str) -> ExtractedPdf:
        raise NotImplementedError
