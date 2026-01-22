from PIL import Image
import hashlib
import io
from typing import Tuple, Optional

class ImageProcessor:
    """Handles image validation, preprocessing, and resizing"""
    
    MAX_SIZE = (1024, 1024)
    ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP', 'GIF'}
    
    def validateImage(self, image_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate image format and basic integrity"""
        try:
            image = Image.open(io.BytesIO(image_data))
            format_name = image.format
            
            if format_name not in self.ALLOWED_FORMATS:
                return False, f"Unsupported format: {format_name}. Allowed: {', '.join(self.ALLOWED_FORMATS)}"
            
            # Check if image can be loaded
            image.verify()
            return True, None
        except Exception as e:
            return False, f"Invalid image: {str(e)}"
    
    def preprocessImage(self, image_data: bytes) -> Image.Image:
        """Preprocess image for AI model (convert to RGB, normalize)"""
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def resizeImage(self, image: Image.Image, max_size: Tuple[int, int] = None) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        if max_size is None:
            max_size = self.MAX_SIZE
        
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    def calculateHash(self, image_data: bytes) -> str:
        """Calculate SHA256 hash of image data for caching"""
        return hashlib.sha256(image_data).hexdigest()

