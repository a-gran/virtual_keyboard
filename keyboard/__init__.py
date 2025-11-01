"""
Пакет виртуальной клавиатуры
Содержит все модули для работы приложения
"""

from .config import Language, UIConfig
from .visualizers import BaseKeyboardVisualizer, EnglishKeyboardVisualizer, RussianKeyboardVisualizer
from .controllers import BaseKeyboardController, EnglishKeyboardController, RussianKeyboardController
from .factory import KeyboardFactory
from .services import LanguageDetector, CapsLockDetector
from .manager import LayoutManager

__all__ = [
    'Language',
    'UIConfig',
    'BaseKeyboardVisualizer',
    'EnglishKeyboardVisualizer',
    'RussianKeyboardVisualizer',
    'BaseKeyboardController',
    'EnglishKeyboardController',
    'RussianKeyboardController',
    'KeyboardFactory',
    'LanguageDetector',
    'CapsLockDetector',
    'LayoutManager',
]

__version__ = '2.0.0'
__author__ = 'Virtual Keyboard Team'