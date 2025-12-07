from __future__ import annotations
import json
from typing import Any

from llama_index.core.llms import ChatMessage, ChatResponse
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.core.prompts import RichPromptTemplate

from sds_digest.src.secrets import Secrets
from sds_digest.llms.prompts import STRUCTURED_SDS_SYSTEM_PROMPT, STRUCTURE_SECTION_PROMPT
from sds_digest.llms.utils import from_chat_response_to_model
from sds_digest.src.processing.processor import (
    Section,
    StructuredSection,
    Sections,
    StructuredSections,
)



class SDSStructureLLM:
    def __init__(
        self,
        llm: OpenAI | Ollama,
        system_prompt: RichPromptTemplate = STRUCTURED_SDS_SYSTEM_PROMPT,
        **kwargs,
    ):
        self.llm = llm
        self.structured_llm = self.llm.as_structured_llm(Sections)
        self.system_prompt = system_prompt


    @classmethod
    def from_openai(cls, model: str = "gpt-4o", **kwargs) -> SDSStructureLLM:
        llm = OpenAI(model=model, api_key=Secrets().openai_api_key, **kwargs)
        return cls(llm=llm, **kwargs)

    @classmethod
    def from_ollama(cls, model: str = "gpt-oss:latest", **kwargs) -> SDSStructureLLM:
        llm = Ollama(model=model, **kwargs)
        return cls(llm=llm, **kwargs)

    def _build_messages(self, text: str) -> list[ChatMessage]:
        return [
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=text),
        ]

    def extract_sections(self, text: str) -> Sections:
        print(f"Extracting sections...")
        messages = self._build_messages(text)
        response: ChatResponse = self.structured_llm.chat(messages=messages)
        try:
            return from_chat_response_to_model(response, Sections)
        except Exception as e:
            print(f"Error converting chat response to model: {e}")
            raise e

    async def aextract_sections(self, text: str) -> Sections:
        print(f"Extracting sections...")
        messages = self._build_messages(text)
        response: ChatResponse = await self.structured_llm.achat(messages=messages)
        try:
            return from_chat_response_to_model(response, Sections)
        except Exception as e:
            print(f"Error converting chat response to model: {e}")
            raise e


class SectionStructureLLM:
    def __init__(
        self,
        llm: OpenAI | Ollama,
        system_prompt: RichPromptTemplate = STRUCTURE_SECTION_PROMPT,
        **kwargs,
    ):
        self.llm = llm
        self.system_prompt = system_prompt

    @classmethod
    def from_openai(cls, model: str = "gpt-4o", **kwargs) -> SectionStructureLLM:
        llm = OpenAI(model=model, api_key=Secrets().openai_api_key, **kwargs)
        return cls(llm=llm, **kwargs)

    @classmethod
    def from_ollama(cls, model: str = "gpt-oss:latest", **kwargs) -> SectionStructureLLM:
        llm = Ollama(model=model, **kwargs)
        return cls(llm=llm, **kwargs)

    def _format_prompt(self, text: str) -> str:
        return self.system_prompt.format(section_content=text)

    def _build_messages(self, text: str) -> list[ChatMessage]:
        prompt = self._format_prompt(text)
        return [
            ChatMessage(role="system", content=prompt),
            ChatMessage(role="user", content="Please structure the given section content into a valid JSON representation"),
        ]
    
    def _response_to_json(self, response: ChatResponse) -> dict[str, Any] | str:
        try:
            # remove ```json\n and \n``` from the response
            response_content = response.message.content.replace("```json\n", "").replace("\n```", "")
            json_response = json.loads(response_content)
            return json_response
        except Exception as e:
            print(f"Error converting chat response to JSON: {e}")
            return response.message.content

    def _maybe_json_to_structured_section(self, response: dict[str, Any] | str, section: Section) -> StructuredSection:
        match response:
            case dict():
                structured_content = response
            case str():
                structured_content = {"section_content": response}
        return StructuredSection(
            section_title=section.section_title,
            section_summary=section.section_summary,
            structured_content=structured_content,
        )

    def structure_section(self, section: Section) -> StructuredSection:
        print(f"Structuring section: {section.section_title}")
        messages = self._build_messages(section.raw_content_of_section)
        response: ChatResponse = self.llm.chat(messages=messages)
        return self._maybe_json_to_structured_section(
            self._response_to_json(response),
            section,
        )

    async def astructure_section(self, section: Section) -> StructuredSection:
        print(f"Structuring section: {section.section_title}")
        messages = self._build_messages(section.raw_content_of_section)
        response: ChatResponse = await self.llm.achat(messages=messages)
        return self._maybe_json_to_structured_section(
            self._response_to_json(response),
            section,
        )
