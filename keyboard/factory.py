"""
Модуль фабрики для создания компонентов клавиатуры
Реализует паттерн Factory для создания визуализаторов и контроллеров
"""

import tkinter as tk
from typing import Tuple

from .config import Language
from .visualizers import BaseKeyboardVisualizer, EnglishKeyboardVisualizer, RussianKeyboardVisualizer
from .controllers import BaseKeyboardController, EnglishKeyboardController, RussianKeyboardController


class KeyboardFactory:
    """Фабрика для создания визуализаторов и контроллеров клавиатуры"""

    @staticmethod
    def create_visualizer(language: Language, root: tk.Tk) -> BaseKeyboardVisualizer:
        """Создание визуализатора по языку"""
        if language == Language.ENGLISH:
            return EnglishKeyboardVisualizer(root)
        elif language == Language.RUSSIAN:
            return RussianKeyboardVisualizer(root)
        else:
            raise ValueError(f"Unsupported language: {language}")

    @staticmethod
    def create_controller(language: Language, visualizer: BaseKeyboardVisualizer) -> BaseKeyboardController:
        """Создание контроллера по языку"""
        if language == Language.ENGLISH:
            return EnglishKeyboardController(visualizer)
        elif language == Language.RUSSIAN:
            return RussianKeyboardController(visualizer)
        else:
            raise ValueError(f"Unsupported language: {language}")

    @staticmethod
    def create_layout(language: Language, root: tk.Tk) -> Tuple[BaseKeyboardVisualizer, BaseKeyboardController]:
        """Создание полной раскладки (визуализатор + контроллер)"""
        visualizer = KeyboardFactory.create_visualizer(language, root)
        controller = KeyboardFactory.create_controller(language, visualizer)
        return visualizer, controller