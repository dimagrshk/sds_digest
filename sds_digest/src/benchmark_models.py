"""Pydantic models for benchmark questions validation."""

from pydantic import BaseModel, Field
from typing import List


class BenchmarkQuestion(BaseModel):
    """Model for a single benchmark question."""
    
    id: int = Field(..., description="Unique identifier for the question")
    section: str = Field(..., description="SDS section number and name")
    reference: str = Field(..., description="Reference text from the SDS")
    reason: str = Field(..., description="Reason for including this question in the benchmark")
    question: str = Field(..., description="The question text")
    example_of_correct_answer: str = Field(..., description="Example of a correct answer")
    description_of_correct_answer: str = Field(..., description="Description of what constitutes a correct answer")


class BenchmarkQuestions(BaseModel):
    """Model for a collection of benchmark questions."""
    
    questions: List[BenchmarkQuestion] = Field(..., description="List of benchmark questions")
    
    @classmethod
    def from_json_file(cls, file_path: str) -> "BenchmarkQuestions":
        """Load benchmark questions from a JSON file."""
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
    
    def to_json_file(self, file_path: str) -> None:
        """Save benchmark questions to a JSON file."""
        import json
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
