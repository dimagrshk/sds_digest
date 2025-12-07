from __future__ import annotations

import asyncio
from sds_digest.src.processing.processor import (
    SafetyDataSheetProcessor,
    ProcessorIdentifier,
    ProcessedSafetyDataSheet,
    StructuredSection,
    StructuredSections,
)
from sds_digest.src.extraction.extractor import ExtractedPdf
from sds_digest.llms.structure_llm import SDSStructureLLM, SectionStructureLLM, Sections
from sds_digest.llms.summary_llm import SummaryLLM




class LLMSafetyDataSheetProcessor(SafetyDataSheetProcessor):

    def __init__(
        self,
        sds_structure_llm: SDSStructureLLM,
        section_structure_llm: SectionStructureLLM,
        summary_llm: SummaryLLM,
    ) -> None:
        self.sds_structure_llm = sds_structure_llm
        self.section_structure_llm = section_structure_llm
        self.summary_llm = summary_llm

    @classmethod
    def from_openai(cls, model: str = "gpt-4o", **kwargs) -> LLMSafetyDataSheetProcessor:
        sds_structure_llm = SDSStructureLLM.from_openai(model=model, **kwargs)
        section_structure_llm = SectionStructureLLM.from_openai(model=model, **kwargs)
        summary_llm = SummaryLLM.from_openai(model=model, **kwargs)
        return cls(sds_structure_llm=sds_structure_llm, section_structure_llm=section_structure_llm, summary_llm=summary_llm)

    @classmethod
    def from_ollama(cls, model: str = "gpt-oss:latest", **kwargs) -> LLMSafetyDataSheetProcessor:
        sds_structure_llm = SDSStructureLLM.from_ollama(model=model, **kwargs)
        section_structure_llm = SectionStructureLLM.from_ollama(model=model, **kwargs)
        summary_llm = SummaryLLM.from_ollama(model=model, **kwargs)
        return cls(sds_structure_llm=sds_structure_llm, section_structure_llm=section_structure_llm, summary_llm=summary_llm)

    def process(self, extracted_pdf: ExtractedPdf) -> ProcessedSafetyDataSheet:
        sds_sections: Sections = self.sds_structure_llm.extract_sections(extracted_pdf.content)
        print(f"Extracted {len(sds_sections.sections)} sections")
        
        structured_sections: list[StructuredSection] = []
        for section in sds_sections.sections:
            structured_section: StructuredSection = self.section_structure_llm.structure_section(section)
            structured_sections.append(structured_section)
        structured_sections = StructuredSections(structured_sections=structured_sections)
        
        summary: str = self.summary_llm.summarize(extracted_pdf.content)
        print("Summary generated")
        
        return ProcessedSafetyDataSheet(
            markdown_content=extracted_pdf.content,
            structured_content=structured_sections,
            summary=summary,
        )

    async def aprocess(self, extracted_pdf: ExtractedPdf) -> ProcessedSafetyDataSheet:
        sds_sections: Sections = await self.sds_structure_llm.aextract_sections(extracted_pdf.content)
        
        # Schedule summary task to run concurrently
        summary_task = asyncio.create_task(self.summary_llm.asummarize(extracted_pdf.content))
        
        semaphore = asyncio.Semaphore(5)
        
        async def process_section_with_semaphore(section):
            async with semaphore:
                return await self.section_structure_llm.astructure_section(section)
        
        structured_sections: list[StructuredSection] = await asyncio.gather(
            *[process_section_with_semaphore(section) for section in sds_sections.sections]
        )
        structured_sections = StructuredSections(structured_sections=structured_sections)
        
        # Await the summary task that was running concurrently
        summary: str = await summary_task
        print("Summary generated")
        return ProcessedSafetyDataSheet(
            markdown_content=extracted_pdf.content,
            structured_content=structured_sections,
            summary=summary,
        )
