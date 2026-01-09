import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel

class UserData(BaseModel):
    uuid: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_pending: Optional[bool] = None
    profile_picture_url: Optional[str] = None
    job_title: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None

    class Config:
        use_enum_values = True


class UserCreateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    is_active: Optional[bool] = True
    is_pending: Optional[bool] = None
    profile_picture_url: Optional[str] = None
    job_title: Optional[str] = None
    business_uuid: Optional[UUID] = None

    class Config:
        use_enum_values = True


class UserDataResponse(BaseModel):
    data: Any
    status_code: int
    message: str

    class Config:
        use_enum_values = True
