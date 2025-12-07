from __future__ import annotations

from llama_index.core.llms import ChatMessage, ChatResponse
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import RichPromptTemplate
from pydantic import BaseModel, Field

from sds_digest.src.secrets import Secrets
from sds_digest.llms.prompts import JUDGE_PROMPT
from sds_digest.llms.utils import from_chat_response_to_model


class Judgment(BaseModel):
    reason: str = Field(..., description="Reason of the judgment, why answer is correct or wrong")
    correctness: bool = Field(..., description="true if answer falls under the acceptence criteria, false if not")


class JudgeLLM:
    def __init__(
        self,
        llm: OpenAI | Ollama,
        system_prompt: RichPromptTemplate = JUDGE_PROMPT,
        **kwargs,
    ):
        self.llm = llm
        self.structured_llm = self.llm.as_structured_llm(Judgment)
        self.system_prompt = system_prompt

    @classmethod
    def from_openai(cls, model: str = "gpt-4o", **kwargs) -> JudgeLLM:
        llm = OpenAI(model=model, api_key=Secrets().openai_api_key, **kwargs)
        return cls(llm=llm, **kwargs)

    @classmethod
    def from_ollama(cls, model: str = "gpt-oss:latest", **kwargs) -> JudgeLLM:
        llm = Ollama(model=model, **kwargs)
        return cls(llm=llm, **kwargs)

    def _format_prompt(self, answer: str, acceptance_criteria: str) -> str:
        return self.system_prompt.format(answer=answer, acceptance_criteria=acceptance_criteria)

    def _build_messages(self, answer: str, acceptance_criteria: str) -> list[ChatMessage]:
        prompt = self._format_prompt(answer, acceptance_criteria)
        return [
            ChatMessage(role="user", content=prompt),
        ]

    def judge(self, answer: str, acceptance_criteria: str) -> Judgment:
        messages = self._build_messages(answer, acceptance_criteria)
        response: ChatResponse = self.structured_llm.chat(messages=messages)
        try:
            return from_chat_response_to_model(response, Judgment)
        except Exception as e:
            print(f"Error converting chat response to model: {e}")
            raise e

    async def ajudge(self, answer: str, acceptance_criteria: str) -> Judgment:
        messages = self._build_messages(answer, acceptance_criteria)
        response: ChatResponse = await self.structured_llm.achat(messages=messages)
        try:
            return from_chat_response_to_model(response, Judgment)
        except Exception as e:
            print(f"Error converting chat response to model: {e}")
            raise e
