from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.schemas.user import UserCreate, UserResponse , UserLogin
from app.utils.security import hash_password , verify_password,create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if a user with this email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Hash the plain-text password securely
    hashed_pwd = hash_password(user.password)
    print ("Hashed Password",hashed_pwd)

    # 3. Create the new User database model instance
    new_user = User(
        email=user.email,
        hashed_password=hashed_pwd
    )

    # 4. Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refreshes to get the generated id and timestamp

    # 5. Return the response (Pydantic automatically strips the password hash out)
    return new_user


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # 1. Query the database for the user by email
    user_record = db.query(User).filter(User.email == user.email).first()
    
    # 2. Verify user exists AND password matches (combined to prevent user enumeration)
    if not user_record or not verify_password(user.password, user_record.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate the JWT access token using the user's email as the subject ('sub')
    access_token = create_access_token(data={"sub": user_record.email})
    
    # 4. Return the token to the client
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }    
   
