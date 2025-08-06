"""Command-line interface for vietcombank-captcha."""

import argparse
import sys
from pathlib import Path
from typing import List

from .predictor import VietcombankCaptcha


def predict_single(args):
    """Handle single image prediction."""
    predictor = VietcombankCaptcha(args.model)
    
    if args.confidence:
        code, confidences = predictor.predict_with_confidence(args.image)
        print(f"Predicted code: {code}")
        print("Confidence per digit:")
        for i, conf in enumerate(confidences):
            print(f"  Digit {i+1}: {conf:.3f}")
        avg_conf = sum(confidences) / len(confidences)
        print(f"Average confidence: {avg_conf:.3f}")
    else:
        code = predictor.predict(args.image)
        print(code)


def predict_batch(args):
    """Handle batch prediction."""
    predictor = VietcombankCaptcha(args.model)
    
    # Get all image files from directory
    image_dir = Path(args.directory)
    if not image_dir.exists():
        print(f"Error: Directory '{args.directory}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Find all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
    image_files = []
    for ext in image_extensions:
        image_files.extend(image_dir.glob(f"*{ext}"))
        image_files.extend(image_dir.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"No image files found in '{args.directory}'", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(image_files)} images...")
    
    # Convert to string paths
    image_paths = [str(f) for f in sorted(image_files)]
    
    # Predict
    if args.confidence:
        results = predictor.predict_batch(image_paths, return_confidence=True)
        for path, (code, confidences) in zip(image_paths, results):
            filename = Path(path).name
            avg_conf = sum(confidences) / len(confidences) if code != "ERROR" else 0.0
            print(f"{filename}: {code} (confidence: {avg_conf:.3f})")
    else:
        results = predictor.predict_batch(image_paths, return_confidence=False)
        for path, code in zip(image_paths, results):
            filename = Path(path).name
            print(f"{filename}: {code}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Vietcombank CAPTCHA Predictor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Predict single image
  vietcombank-captcha predict captcha.png
  
  # Predict with confidence scores
  vietcombank-captcha predict captcha.png --confidence
  
  # Batch prediction
  vietcombank-captcha predict-batch ./captcha_folder/
  
  # Use custom model
  vietcombank-captcha predict captcha.png --model custom_model.onnx
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single prediction command
    predict_parser = subparsers.add_parser('predict', help='Predict single image')
    predict_parser.add_argument('image', help='Path to captcha image')
    predict_parser.add_argument('--confidence', '-c', action='store_true',
                               help='Show confidence scores')
    predict_parser.add_argument('--model', '-m', help='Path to custom ONNX model')
    
    # Batch prediction command
    batch_parser = subparsers.add_parser('predict-batch', help='Predict multiple images')
    batch_parser.add_argument('directory', help='Directory containing images')
    batch_parser.add_argument('--confidence', '-c', action='store_true',
                             help='Show confidence scores')
    batch_parser.add_argument('--model', '-m', help='Path to custom ONNX model')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'predict':
            predict_single(args)
        elif args.command == 'predict-batch':
            predict_batch(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()