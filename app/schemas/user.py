from datetime import datetime
from pydantic import BaseModel, EmailStr

# 1. Schema for when a user registers (Incoming data)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 2. Schema for what we return back to the client (Outgoing data)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read directly from SQLAlchemy models