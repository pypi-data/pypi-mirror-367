# finetuner/__init__.py

"""
No-Code LLM Fine-Tuner

A Python library and platform to fine-tune language models with no code,
using local or cloud-based resources.
"""

# Import the core classes to make them directly accessible from the package
from .config import Config
from .data_loader import DataLoader
from .model_manager import ModelManager
from .trainer import Trainer

# You can also define package-level information
__version__ = "0.0.11"
__author__ = "Minerva AI"

# The __all__ variable tells Python what to import when a user runs `from finetuner import *`
__all__ = [
    'Config',
    'DataLoader',
    'ModelManager',
    'Trainer'
]
