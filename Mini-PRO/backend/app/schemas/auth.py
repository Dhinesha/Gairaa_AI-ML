import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSignUpRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128, description="User full name")
    email: str = Field(..., description="Unique user email address")
    password: str = Field(..., min_length=4, max_length=128, description="User password")
    role: str = Field(default="student", description="Role: student, developer, security_lead")
    organization: Optional[str] = Field(default="Department of AI & Data Science", description="User organization")


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Registered user email")
    password: str = Field(..., description="User password")
    role: Optional[str] = Field(default=None, description="Optional persona override")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: str
    organization: str
    is_active: bool
    created_at: datetime.datetime

