"""
NDS SaveCraftr - Universal Nintendo DS Save File Craftr

A smart utility to craft DS save files between different formats and sizes.
Automatically detects whether to expand (for TWiLight Menu++) or trim (for flashcarts).
"""

from .cli import convert_save, find_actual_data_end, smart_trim_size

__version__ = "1.0.0"
__author__ = "tcsenpai"
__description__ = "Universal Nintendo DS Save File Craftr"

__all__ = ["convert_save", "find_actual_data_end", "smart_trim_size", "__version__"]