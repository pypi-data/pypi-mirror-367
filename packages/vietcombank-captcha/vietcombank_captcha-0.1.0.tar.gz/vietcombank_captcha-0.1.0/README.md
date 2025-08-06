# vietcombank-captcha

A lightweight Python library for solving Vietcombank CAPTCHA images using ONNX runtime. This project is purely educational. Using synthetic data from various sources.

## Features

- 🚀 Fast inference using ONNX runtime
- 🎯 High accuracy (>95% on test set)
- 🔧 Simple API with minimal dependencies
- 📦 Lightweight package (~2.2MB model)
- 🖼️ Supports multiple input formats (file path, PIL Image, numpy array)
- 🔢 Batch prediction support
- 🍎 Optimized for Apple M Chip

## Installation

### Using pip

```bash
pip install vietcombank-captcha
```

### Using UV (recommended)

```bash
uv pip install vietcombank-captcha
```

## Quick Start

### Basic Usage

```python
from vietcombank_captcha import predict

# Predict from image file
captcha_code = predict("captcha.png")
print(f"Predicted code: {captcha_code}")
```

### Advanced Usage

```python
from vietcombank_captcha import VietcombankCaptcha

# Initialize predictor
predictor = VietcombankCaptcha()

# Predict single image with confidence scores
code, confidences = predictor.predict_with_confidence("captcha.png")
print(f"Code: {code}")
print(f"Confidence per digit: {confidences}")

# Batch prediction
images = ["captcha1.png", "captcha2.png", "captcha3.png"]
results = predictor.predict_batch(images)
print(f"Results: {results}")

# With confidence scores
results_with_conf = predictor.predict_batch(images, return_confidence=True)
for code, conf in results_with_conf:
    print(f"Code: {code}, Avg confidence: {sum(conf)/len(conf):.2f}")
```

### Using PIL Image

```python
from PIL import Image
from vietcombank_captcha import predict

# Load image with PIL
img = Image.open("captcha.png")
code = predict(img)
print(f"Code: {code}")
```

### Using numpy array

```python
import numpy as np
from vietcombank_captcha import predict

# From numpy array (H, W, 3) RGB format
img_array = np.array(...)  # Your image array
code = predict(img_array)
print(f"Code: {code}")
```

## Command Line Interface

```bash
# Predict single image
vietcombank-captcha predict image.png

# Predict with confidence scores
vietcombank-captcha predict image.png --confidence

# Batch prediction
vietcombank-captcha predict-batch ./captcha_folder/

# Use custom model
vietcombank-captcha predict image.png --model custom_model.onnx
```

## API Reference

### `VietcombankCaptcha`

Main predictor class.

#### `__init__(model_path: Optional[str] = None)`
Initialize the predictor with an optional custom model path.

#### `predict(image) -> str`
Predict CAPTCHA code from an image.

#### `predict_with_confidence(image) -> Tuple[str, List[float]]`
Predict with confidence scores for each digit.

#### `predict_batch(images, return_confidence=False)`
Predict multiple images at once.

### `predict(image, model_path=None) -> str`

Convenience function for single prediction.

## Requirements

- Python >= 3.8
- numpy >= 1.20.0
- Pillow >= 9.0.0
- onnxruntime >= 1.16.0

## Model Information

- Input: RGB image (155x50 pixels)
- Output: 5-digit code (0-9)
- Model size: ~2.2MB
- Architecture: Multi-output CNN optimized for CAPTCHA recognition

## Performance

- Inference time: ~5-10ms per image (CPU)
- Accuracy: >95% on test dataset
- Memory usage: <100MB

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/bangprovn/vietcombank-captcha/issues).