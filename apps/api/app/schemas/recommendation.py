from pydantic import BaseModel
from typing import List

class RecommendationRequest(BaseModel):
    city: str
    scene: str
    target_style: str

class OutfitRecommendation(BaseModel):
    outfit_id: str
    score: float
    reason: str
    
class RecommendationResponse(BaseModel):
    recommendations: List[OutfitRecommendation]
