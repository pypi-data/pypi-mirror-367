"""Vietcombank CAPTCHA Predictor - Lightweight ONNX-based prediction library."""

import os
from pathlib import Path
from typing import Optional, Tuple, List, Union
import numpy as np
from PIL import Image

# Constants
IMAGE_WIDTH = 155
IMAGE_HEIGHT = 50
NUM_DIGITS = 5
NUM_CLASSES = 10


class VietcombankCaptcha:
    """Lightweight CAPTCHA predictor for Vietcombank CAPTCHAs using ONNX runtime."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the CAPTCHA predictor.
        
        Args:
            model_path: Path to the ONNX model file. If None, uses the bundled model.
        """
        try:
            import onnxruntime as ort
        except ImportError:
            raise ImportError(
                "onnxruntime is required. Install with: pip install onnxruntime"
            )
        
        self.ort = ort
        
        if model_path is None:
            # Use bundled model
            model_path = Path(__file__).parent / "models" / "vietcombank_captcha.onnx"
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Bundled model not found at {model_path}. "
                    "Please provide a model path or reinstall the package."
                )
        
        self.model_path = str(model_path)
        self._load_model()
    
    def _load_model(self):
        """Load the ONNX model."""
        # Use CPU provider for maximum compatibility
        providers = ['CPUExecutionProvider']
        
        # Check for CoreML on macOS
        if os.uname().sysname == 'Darwin':
            try:
                providers.insert(0, 'CoreMLExecutionProvider')
            except:
                pass
        
        self.session = self.ort.InferenceSession(self.model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [output.name for output in self.session.get_outputs()]
    
    def preprocess_image(self, image: Union[str, Path, Image.Image, np.ndarray]) -> np.ndarray:
        """
        Preprocess an image for prediction.
        
        Args:
            image: Can be a file path, PIL Image, or numpy array
            
        Returns:
            Preprocessed image array ready for model input
        """
        # Handle different input types
        if isinstance(image, (str, Path)):
            img = Image.open(image)
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            img = image
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to model input size
        img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize
        img_array = np.array(img, dtype=np.float32)
        img_array = img_array / 255.0
        
        return img_array
    
    def predict(self, image: Union[str, Path, Image.Image, np.ndarray]) -> str:
        """
        Predict the CAPTCHA code from an image.
        
        Args:
            image: Input image (file path, PIL Image, or numpy array)
            
        Returns:
            Predicted CAPTCHA code as a string
        """
        result, _ = self.predict_with_confidence(image)
        return result
    
    def predict_with_confidence(
        self, 
        image: Union[str, Path, Image.Image, np.ndarray]
    ) -> Tuple[str, List[float]]:
        """
        Predict the CAPTCHA code with confidence scores.
        
        Args:
            image: Input image (file path, PIL Image, or numpy array)
            
        Returns:
            Tuple of (predicted_code, confidence_scores_per_digit)
        """
        # Preprocess the image
        img_array = self.preprocess_image(image)
        img_batch = np.expand_dims(img_array, axis=0)
        
        # Run inference
        outputs = self.session.run(self.output_names, {self.input_name: img_batch})
        
        # Extract predictions
        predicted_digits = []
        confidence_scores = []
        
        for i in range(NUM_DIGITS):
            digit_probs = outputs[i][0]
            predicted_digit = np.argmax(digit_probs)
            confidence = float(digit_probs[predicted_digit])
            
            predicted_digits.append(str(predicted_digit))
            confidence_scores.append(confidence)
        
        predicted_code = ''.join(predicted_digits)
        
        return predicted_code, confidence_scores
    
    def predict_batch(
        self, 
        images: List[Union[str, Path, Image.Image, np.ndarray]],
        return_confidence: bool = False
    ) -> Union[List[str], List[Tuple[str, List[float]]]]:
        """
        Predict CAPTCHA codes for multiple images.
        
        Args:
            images: List of images (file paths, PIL Images, or numpy arrays)
            return_confidence: If True, return confidence scores along with predictions
            
        Returns:
            List of predicted codes, or list of (code, confidence) tuples if return_confidence=True
        """
        results = []
        
        for image in images:
            try:
                if return_confidence:
                    result = self.predict_with_confidence(image)
                else:
                    result = self.predict(image)
                results.append(result)
            except Exception as e:
                # Return error placeholder
                if return_confidence:
                    results.append(("ERROR", [0.0] * NUM_DIGITS))
                else:
                    results.append("ERROR")
        
        return results


def predict(image: Union[str, Path, Image.Image, np.ndarray], model_path: Optional[str] = None) -> str:
    """
    Convenience function to predict a single CAPTCHA.
    
    Args:
        image: Input image
        model_path: Optional path to ONNX model
        
    Returns:
        Predicted CAPTCHA code
    """
    predictor = VietcombankCaptcha(model_path)
    return predictor.predict(image)