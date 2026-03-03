from pydantic import BaseModel

class RegenerationRequest(BaseModel):
    choosen_url: str
    feedback_prompt: str

class FeedbackRequest(BaseModel):
    image_url: str
    like: bool   # True = like, False = dislike
    stage: str   # Colour_Theme|Graphics|Product_Placement

class ChoosenRequest(BaseModel):
    choosen_url: str
    score: int

class GraphicsRefinementRequest(BaseModel):
    selected_graphics_url: str
    feedback_prompt: str