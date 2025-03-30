from datetime import datetime
from pydantic import BaseModel

class ExpiredLinkBase(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime
    expired_at: datetime
    total_clicks: int
    project: str | None

class ExpiredLinkResponse(ExpiredLinkBase):
    id: int
    user_id: int | None

    class Config:
        orm_mode = True