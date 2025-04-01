from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class LinkBase(BaseModel):
    original_url: str
    username: str
    custom_alias: Optional[str] = Field(None, max_length=50)
    expires_at: Optional[datetime] = None
    project: Optional[str] = None


class LinkCreate(LinkBase):
    pass


class PublicLinkCreate(BaseModel):
    original_url: str
    expires_at: datetime | None = None
    project: str | None = None


class LinkUpdate(BaseModel):
    original_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class LinkCodeUpdate(BaseModel):
    short_code: str = Field(min_length=3, max_length=32)


class LinkResponse(LinkBase):
    original_url: str
    short_code: str
    created_at: datetime
    clicks: int
    last_clicked_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True
