import bcrypt

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