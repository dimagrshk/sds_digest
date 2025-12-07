from __future__ import annotations

from llama_index.core.llms import ChatMessage, ChatResponse
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import RichPromptTemplate

from sds_digest.src.secrets import Secrets
from sds_digest.llms.prompts import FULL_SDS_SYSTEM_PROMPT


class SummaryLLM:
    def __init__(
        self,
        llm: OpenAI | Ollama,
        system_prompt: RichPromptTemplate = FULL_SDS_SYSTEM_PROMPT,
        **kwargs,
    ):
        self.llm = llm
        self.system_prompt = system_prompt

    @classmethod
    def from_openai(cls, model: str = "gpt-4o", **kwargs) -> SummaryLLM:
        llm = OpenAI(model=model, api_key=Secrets().openai_api_key, **kwargs)
        return cls(llm=llm, **kwargs)

    @classmethod
    def from_ollama(cls, model: str = "gpt-oss:latest", **kwargs) -> SummaryLLM:
        llm = Ollama(model=model, **kwargs)
        return cls(llm=llm, **kwargs)

    def _format_prompt(self, sds_info: str) -> str:
        return self.system_prompt.format(sds_info=sds_info)

    def _build_messages(self, sds_info: str) -> list[ChatMessage]:
        system_content = self._format_prompt(sds_info)
        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(role="user", content=f"Please provide a summary of the chemical substance described in the given Safety Data Sheet"),
        ]

    def summarize(self, sds_info: str) -> str:
        messages = self._build_messages(sds_info)
        response: ChatResponse = self.llm.chat(messages=messages)
        return response.message.content

    async def asummarize(self, sds_info: str) -> str:
        messages = self._build_messages(sds_info)
        response: ChatResponse = await self.llm.achat(messages=messages)
        return response.message.content

