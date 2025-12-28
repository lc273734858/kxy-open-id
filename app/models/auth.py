from pydantic import BaseModel, Field


class InitUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, max_length=100, description="Password")


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    token: str = Field(..., description="JWT token")
    username: str = Field(..., description="Username")


class CheckInitResponse(BaseModel):
    initialized: bool = Field(..., description="Whether system is initialized")
