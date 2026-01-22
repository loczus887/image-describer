from typing import Tuple, Optional

class ValidationService:
    """Handle file size and format validation"""

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif'
    }
    
    def validateFileSize(self, file_size: int) -> Tuple[bool, Optional[str]]:
        """Validate file size"""
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum of {self.MAX_FILE_SIZE / (1024*1024):.1f} MB"
        if file_size == 0:
            return False, "File is empty"
        return True, None
    
    def validateMimeType(self, mime_type: str) -> Tuple[bool, Optional[str]]:
        """Validate MIME type"""
        if mime_type not in self.ALLOWED_MIME_TYPES:
            return False, f"Unsupported MIME type: {mime_type}. Allowed: {', '.join(self.ALLOWED_MIME_TYPES)}"
        return True, None
    
    def validateImageFile(self, file_size: int, mime_type: str) -> Tuple[bool, Optional[str]]:
        """Comprehensive validation of image file"""
        # Check file size
        valid, error = self.validateFileSize(file_size)
        if not valid:
            return False, error
        
        # Check MIME type
        valid, error = self.validateMimeType(mime_type)
        if not valid:
            return False, error
        
        return True, None

