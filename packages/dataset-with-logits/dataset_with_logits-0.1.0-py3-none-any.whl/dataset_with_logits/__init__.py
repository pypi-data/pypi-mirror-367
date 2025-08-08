"""
Dataset with Logits

A PyTorch package for loading computer vision datasets paired with pre-computed model logits.
Perfect for knowledge distillation, model analysis, and efficient research workflows.
"""

from .datasets import ImageNet
from .utils import list_available_models, download_predictions

__version__ = "0.1.0"
__author__ = "ViGeng"
__email__ = "your.email@example.com"

__all__ = [
    "ImageNet",
    "list_available_models",
    "download_predictions"
]
