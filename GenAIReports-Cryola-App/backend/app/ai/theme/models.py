from typing import List, Literal
from pydantic import BaseModel, Field

class EvaluationItem(BaseModel):
    image_id: str
    confidence_score: float = Field(..., ge=0, le=100)
    feedback: str

class EvaluatorOutput(BaseModel):
    evaluation: List[EvaluationItem]
    regenerate_required: Literal["yes", "no"]

class RefinementEvaluationResult(BaseModel):
    confidence_score: int
    explanation: str
    regeneration_required: Literal["yes", "no"]

class FeedbackAnalyzerOutput(BaseModel):
    refined_prompt: str