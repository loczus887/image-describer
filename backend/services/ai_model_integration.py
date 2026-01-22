from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from typing import Optional

class AIModelIntegration:
    """Integration with local BLIP model for image captioning"""
    
    def __init__(self):
        self.model_name = "Salesforce/blip-image-captioning-base"
        self.processor: Optional[BlipProcessor] = None
        self.model: Optional[BlipForConditionalGeneration] = None
        self._loaded = False
    
    def _load_model(self):
        """Lazy load the model on first use"""
        if not self._loaded:
            try:
                print(f"[AIModel] Loading model: {self.model_name}")
                print("[AIModel] This may take a few minutes on first run...")
                self.processor = BlipProcessor.from_pretrained(self.model_name)
                print("[AIModel] Processor loaded")
                self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
                print("[AIModel] Model loaded")
                # Use CPU by default, can be changed to CUDA if available
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"[AIModel] Using device: {self.device}")
                self.model.to(self.device)
                self.model.eval()
                self._loaded = True
                print(f"[AIModel] Model successfully loaded on {self.device}")
            except Exception as e:
                import traceback
                print(f"[AIModel] Error loading model: {str(e)}")
                print(f"[AIModel] Traceback: {traceback.format_exc()}")
                raise
    
    def generateDescription(self, image: Image.Image) -> str:
        """Generate description for an image using local BLIP model"""
        try:
            print("[AIModel] Starting description generation...")
            self._load_model()
            
            if not self._loaded or self.processor is None or self.model is None:
                raise RuntimeError("Model not loaded properly")
            
            # Process image
            print("[AIModel] Processing image with processor...")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            print("[AIModel] Image processed, generating caption...")
            
            # Generate caption
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=50)
            
            # Decode the generated text
            description = self.processor.decode(out[0], skip_special_tokens=True)
            print(f"[AIModel] Generated description: {description}")
            return description
        except Exception as e:
            import traceback
            error_msg = f"Error generating description: {str(e)}"
            print(f"[AIModel] {error_msg}")
            print(f"[AIModel] Traceback: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e
    
    def isModelLoaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded

