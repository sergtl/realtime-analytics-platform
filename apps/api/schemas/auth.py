from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(max_length=320, min_length=5)
    password: str = Field(max_length=256, min_length=1)


class RegisterResponse(BaseModel):
    id: int
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=320, min_length=5)
    password: str = Field(max_length=256, min_length=1)


class LoginResponse(BaseModel):
    id: int
    email: EmailStr


class MeResponse(BaseModel):
    id: int
    email: EmailStr


class LogoutResponse(BaseModel):
    ok: bool
