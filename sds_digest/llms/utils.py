from pydantic import BaseModel
from llama_index.core.llms import ChatResponse

def from_chat_response_to_model(chat_response: ChatResponse, model: BaseModel) -> BaseModel:
    return model.model_validate_json(chat_response.message.content)
