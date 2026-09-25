import bcrypt
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as a standard UTF-8 string to store in the database
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode('utf-8')
    if len(plain_bytes) > 72:
        plain_bytes = plain_bytes[:72]
        
    return bcrypt.checkpw(plain_bytes, hashed_password.encode('utf-8'))


# In production, this should be kept in a secure .env file!

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    # Copy the payload data so we don't mutate the original dictionary
    token_payload = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    token_payload.update({"exp": expire})
    
    # Encode into a signed JWT string
    encoded_jwt = jwt.encode(token_payload, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt
