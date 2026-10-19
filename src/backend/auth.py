from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from models import User
from database import SessionLocal

load_dotenv()

# Security
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-focusflow-v1")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_admin_token(user_id: int) -> str:
    """Create admin token"""
    return create_access_token({"sub": str(user_id), "admin": True})

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "user_id": int(user_id),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "role": payload.get("role", "user")
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
    """Get current user from token, automatically ensuring user existence across serverless containers"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload["user_id"]
    username = payload.get("username") or f"user_{user_id}"
    email = payload.get("email") or f"{username}@example.com"
    role = payload.get("role", "user")
    
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = db.query(User).filter(User.username == username).first()
        
    if not user:
        # On serverless (Vercel Lambda), each container has independent ephemeral /tmp storage.
        # Since this JWT is cryptographically verified by our SECRET_KEY, we ensure the user
        # record exists in this container's SQLite database so all queries succeed.
        try:
            user = User(
                id=user_id,
                username=username,
                email=email,
                hashed_password="jwt_verified_user",
                role=role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            user = db.query(User).filter(User.id == user_id).first() or db.query(User).filter(User.username == username).first()

    db.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User session could not be verified"
        )
    
    return user
