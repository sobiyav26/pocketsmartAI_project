from typing import Any
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    rooms: list[str] = Field(min_length=1)
    items: dict[str, int] = {}
    style: str = Field(default="Modern", max_length=80)
    notes: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0, le=10000)
    event_type: str = Field(min_length=2, max_length=80)
    venue: str = Field(default="Home", max_length=120)
    city: str = Field(default="", max_length=120)
    preferences: str = Field(default="", max_length=1000)
