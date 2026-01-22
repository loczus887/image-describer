from sqlalchemy.orm import Session
# Don't import PIL here - lazy load
from typing import Optional, Tuple
from ..data.repositories import DescriptionRepository, UserRepository
from ..data.cache_manager import CacheManager
# Lazy import ImageProcessor to avoid loading PIL at module import
# from .image_processor import ImageProcessor
# Lazy import - don't import AIModelIntegration here to avoid loading transformers at startup
# from .ai_model_integration import AIModelIntegration
from .validation_service import ValidationService

class DescriptionService:
    """Orchestrates the flow between ImageProcessor, AIModelIntegration, and DescriptionRepository"""
    
    def __init__(self, db: Session):
        self.db = db
        self.image_processor = None  # Lazy load
        self.ai_model = None  # Lazy load
        self.validation_service = ValidationService()
        self.description_repo = DescriptionRepository(db)
        self.user_repo = UserRepository(db)
        self.cache_manager = CacheManager()
    
    def _get_image_processor(self):
        """Lazy load ImageProcessor only when needed"""
        if self.image_processor is None:
            from .image_processor import ImageProcessor
            self.image_processor = ImageProcessor()
        return self.image_processor
    
    def _get_ai_model(self):
        """Lazy load AI model only when needed"""
        if self.ai_model is None:
            from .ai_model_integration import AIModelIntegration
            self.ai_model = AIModelIntegration()
        return self.ai_model
    
    def processImage(self, image_data: bytes, user_id: int = 1) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process image and generate description.
        Returns: (success, description, error_message)
        """
        try:
            print(f"[DescriptionService] Processing image, size: {len(image_data)} bytes")
            
            # Validate file
            file_size = len(image_data)
            # Basic MIME type check (would need to be passed from controller)
            valid, error = self.validation_service.validateFileSize(file_size)
            if not valid:
                print(f"[DescriptionService] File size validation failed: {error}")
                return False, None, error
            
            # Get image processor (lazy load)
            image_processor = self._get_image_processor()
            
            # Check cache first
            image_hash = image_processor.calculateHash(image_data)
            print(f"[DescriptionService] Image hash: {image_hash[:16]}...")
            cached_description = self.cache_manager.get(image_hash)
            if cached_description:
                print("[DescriptionService] Found cached description")
                # Save to database if not already there
                existing = self.description_repo.findByImageHash(image_hash)
                if not existing:
                    self.description_repo.create(user_id, image_hash, cached_description)
                return True, cached_description, None
            
            # Validate image format
            print("[DescriptionService] Validating image format...")
            valid, error = image_processor.validateImage(image_data)
            if not valid:
                print(f"[DescriptionService] Image validation failed: {error}")
                return False, None, error
            
            # Preprocess image
            print("[DescriptionService] Preprocessing image...")
            image = image_processor.preprocessImage(image_data)
            image = image_processor.resizeImage(image)
            print(f"[DescriptionService] Image preprocessed, size: {image.size}")
            
            # Generate description using local AI
            print("[DescriptionService] Generating description with AI model...")
            ai_model = self._get_ai_model()
            description = ai_model.generateDescription(image)
            print(f"[DescriptionService] Generated description: {description}")
            
            # Cache the result
            self.cache_manager.set(image_hash, description)
            
            # Save to database
            self.description_repo.create(user_id, image_hash, description)
            
            return True, description, None
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[DescriptionService] Error processing image: {str(e)}")
            print(f"[DescriptionService] Traceback: {error_trace}")
            return False, None, f"Error processing image: {str(e)}"
    
    def getHistory(self, user_id: int, limit: int = 10):
        """Get description history for a user"""
        return self.description_repo.findByUserId(user_id, limit)

