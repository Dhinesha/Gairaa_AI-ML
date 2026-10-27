from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class EmployeeCreate(BaseModel):

    name: str = Field(..., min_length=1, max_length=100, examples=["Dhinesha G"])
    email: str = Field(..., max_length=100, examples=["dhinesha@example.com"])
    department: str = Field(..., min_length=1, max_length=50, examples=["Engineering"])
    role: str = Field(..., min_length=1, max_length=50, examples=["Backend Developer"])
    salary: float = Field(..., gt=0, examples=[75000.0])


class EmployeeUpdate(BaseModel):

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[str] = Field(None, min_length=1, max_length=50)
    salary: Optional[float] = Field(None, gt=0)


class EmployeeResponse(BaseModel):

    id: int
    name: str
    email: str
    department: str
    role: str
    salary: float

    model_config = {"from_attributes": True}
