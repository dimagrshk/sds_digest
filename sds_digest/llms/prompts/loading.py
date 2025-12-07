import os
from llama_index.core.prompts import RichPromptTemplate


def load_prompt(file_path: str) -> RichPromptTemplate:
    with open(file_path, "r") as f:
        return RichPromptTemplate(f.read())
    
local_path = os.path.join(os.path.dirname(__file__), "templates")

FULL_SDS_SYSTEM_PROMPT = load_prompt(os.path.join(local_path, "FULL_SDS_SYSTEM_PROMPT.md"))
JUDGE_PROMPT = load_prompt(os.path.join(local_path, "JUDGE_PROMPT.md"))
STRUCTURED_SDS_SYSTEM_PROMPT = load_prompt(os.path.join(local_path, "STRUCTURED_SDS_SYSTEM_PROMPT.md"))
STRUCTURE_SECTION_PROMPT = load_prompt(os.path.join(local_path, "STRUCTURE_SECTION_PROMPT.md"))
