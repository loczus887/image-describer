from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Tuple
from sqlalchemy.orm import Session
import os

from ..data.database import User
from ..data.repositories import UserRepository

class AuthService:
    """Handle authentication and authorization"""

    # Configuration from environment variables
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username and password"""
        user = self.user_repo.findByUsername(username)
        if not user:
            return None
        if not user.is_active:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """Register a new user"""
        # Validate input
        if len(password) < 8:
            return False, None, "Password must be at least 8 characters"

        if len(username) < 3:
            return False, None, "Username must be at least 3 characters"

        # Check if username exists
        if self.user_repo.findByUsername(username):
            return False, None, "Username already exists"

        # Check if email exists
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            return False, None, "Email already registered"

        # Create user with hashed password
        try:
            password_hash = self.hash_password(password)
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role="user",
                is_active=True
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return True, user, None
        except Exception as e:
            self.db.rollback()
            return False, None, f"Registration failed: {str(e)}"
