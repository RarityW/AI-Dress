from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    db_status: str
    ai_api_status: str
