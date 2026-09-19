from pydantic import BaseModel, ConfigDict
import uuid
from typing import Optional, Dict, Any, List

class ClothingItemBase(BaseModel):
    category: str
    sub_category: str
    primary_color: str
    style: str
    thickness: str
    temp_min: float
    temp_max: float
    
class ClothingItemCreate(ClothingItemBase):
    image_url: str
    secondary_color: Optional[str] = None
    season: Dict[str, Any]
    raw_vlm_attributes: Optional[Dict[str, Any]] = None

class ClothingItemResponse(ClothingItemBase):
    id: uuid.UUID
    user_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
