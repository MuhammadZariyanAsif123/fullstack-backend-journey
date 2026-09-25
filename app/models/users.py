from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # 1. Hashed password column: stores our encrypted pass, cannot be blank
    hashed_password = Column(String, nullable=False)
    
    # 2. Timestamp: automatically stamps the current server time upon creation
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    