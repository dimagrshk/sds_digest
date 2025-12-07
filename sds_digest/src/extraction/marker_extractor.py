from typing import Any

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from sds_digest.src.extraction.extractor import ExtractedPdf



class MarkerExtractor:

    def __init__(self, artifact_dict: dict[str, Any] | None = None):
        self.converter = PdfConverter(
            artifact_dict=artifact_dict or create_model_dict(),
        )

    def extract_pdf(self, pdf_path: str) -> ExtractedPdf:
        rendered = self.converter(pdf_path)
        text, _, images = text_from_rendered(rendered)
        return ExtractedPdf(
            content=text,
            source_file_path=pdf_path,
        )
