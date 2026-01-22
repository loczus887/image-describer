from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from .database import User, Preferences, Description

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def executeQuery(self, query: str, params: dict = None):
        """Execute a raw query"""
        return self.db.execute(query, params or {})
    
    def findById(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def findByUsername(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def create(self, username: str, email: str) -> User:
        user = User(username=username, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

class PreferencesRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def executeQuery(self, query: str, params: dict = None):
        """Execute a raw query"""
        return self.db.execute(query, params or {})
    
    def findByUserId(self, user_id: int) -> Optional[Preferences]:
        return self.db.query(Preferences).filter(Preferences.user_id == user_id).first()
    
    def createOrUpdate(self, user_id: int, high_contrast: bool = False, 
                      font_size: str = "medium", audio_enabled: bool = True) -> Preferences:
        pref = self.findByUserId(user_id)
        if pref:
            pref.high_contrast = high_contrast
            pref.font_size = font_size
            pref.audio_enabled = audio_enabled
        else:
            pref = Preferences(
                user_id=user_id,
                high_contrast=high_contrast,
                font_size=font_size,
                audio_enabled=audio_enabled
            )
            self.db.add(pref)
        self.db.commit()
        self.db.refresh(pref)
        return pref

class DescriptionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def executeQuery(self, query: str, params: dict = None):
        """Execute a raw query"""
        return self.db.execute(query, params or {})
    
    def create(self, user_id: int, image_hash: str, description: str) -> Description:
        desc = Description(user_id=user_id, image_hash=image_hash, description=description)
        self.db.add(desc)
        self.db.commit()
        self.db.refresh(desc)
        return desc
    
    def findByUserId(self, user_id: int, limit: int = 10) -> List[Description]:
        return self.db.query(Description).filter(
            Description.user_id == user_id
        ).order_by(desc(Description.created_at)).limit(limit).all()
    
    def findByImageHash(self, image_hash: str) -> Optional[Description]:
        return self.db.query(Description).filter(Description.image_hash == image_hash).first()

