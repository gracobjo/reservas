from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    
    class Config:
        from_attributes = True
