import uuid
from fastapi_users import schemas
from typing import Optional
from pydantic import Field


class UserRead(schemas.BaseUser[uuid.UUID]):
    #id: int
    #email: str
    username: str
    #is_active: bool
    #is_superuser: bool
    #is_verified: bool


class UserCreate(schemas.BaseUserCreate):
    #email: str
    username: str = Field(..., min_length=3, max_length=50)
    #password: str


#class UserUpdate(schemas.BaseUserUpdate):
    #username: Optional[str] = Field(None, min_length=3, max_length=50)
    #password: Optional[str]
    #email: Optional[str]
    #is_active: Optional[bool]
    #is_superuser: Optional[bool]
    #s_verified: Optional[bool]
