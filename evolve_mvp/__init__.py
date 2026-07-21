"""
evolve_mvp/__init__.py
"""
from .core import VERSION, build_protocol, load_lessons, add_lesson, save_lessons, BEHAVIORAL_GUARDS
from .cli import main

__version__ = VERSION
__all__ = ["main", "VERSION", "build_protocol", "load_lessons", "add_lesson",
           "save_lessons", "BEHAVIORAL_GUARDS"]
