"""
Модуль менеджера раскладок
Управляет переключением между раскладками клавиатуры
"""

import tkinter as tk
import threading
import time
from typing import Dict, Tuple, Optional
from pynput import keyboard

from .config import Language
from .visualizers import BaseKeyboardVisualizer
from .controllers import BaseKeyboardController
from .factory import KeyboardFactory
from .services import LanguageDetector


class LayoutManager:
    """Менеджер для переключения между раскладками"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_language = Language.ENGLISH
        self.layouts: Dict[Language, Tuple[BaseKeyboardVisualizer, BaseKeyboardController]] = {}
        self.current_visualizer: Optional[BaseKeyboardVisualizer] = None
        self.current_controller: Optional[BaseKeyboardController] = None
        self.listener: Optional[keyboard.Listener] = None

        self._initialize_layouts()
        self._start_monitoring()

    def _initialize_layouts(self):
        """Инициализация всех раскладок"""
        for lang in Language:
            visualizer, controller = KeyboardFactory.create_layout(lang, self.root)
            self.layouts[lang] = (visualizer, controller)

        # Устанавливаем текущую раскладку
        self.current_visualizer, self.current_controller = self.layouts[self.current_language]

    def _start_monitoring(self):
        """Запуск мониторинга раскладки и слушателя клавиатуры"""
        layout_monitor_thread = threading.Thread(target=self._monitor_layout, daemon=True)
        layout_monitor_thread.start()

        listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        listener_thread.start()

    def _monitor_layout(self):
        """Мониторинг изменения раскладки клавиатуры"""
        while True:
            try:
                new_language = LanguageDetector.get_current_language()
                if new_language != self.current_language:
                    self.current_language = new_language
                    self.root.after(0, self.switch_layout)
                time.sleep(0.1)
            except Exception:
                time.sleep(0.1)

    def switch_layout(self):
        """Переключение раскладки"""
        # Сохраняем текущий текст
        current_text = self.current_controller.get_typed_text()

        # Останавливаем текущий слушатель
        if self.listener:
            self.listener.stop()

        # Удаляем main_frame текущего визуализатора
        if self.current_visualizer.main_frame is not None:
            self.current_visualizer.main_frame.destroy()
            self.current_visualizer.main_frame = None

        # Переключаем на новую раскладку
        self.current_visualizer, self.current_controller = self.layouts[self.current_language]

        # Синхронизируем состояние Caps Lock перед использованием контроллера
        self.current_controller.sync_caps_lock_state()

        # Передаем сохраненный текст в новый контроллер
        self.current_controller.set_typed_text(current_text)

        # Создаем клавиатуру с сохраненным текстом
        self.current_visualizer.create_keyboard(current_text)

        # Перезапускаем слушатель с новым контроллером
        self.listener = keyboard.Listener(
            on_press=self.current_controller.on_press,
            on_release=self.current_controller.on_release
        )
        self.listener.start()

    def _start_listener(self):
        """Запуск первого слушателя клавиатуры"""
        time.sleep(0.5)  # Даем время на инициализацию
        self.listener = keyboard.Listener(
            on_press=self.current_controller.on_press,
            on_release=self.current_controller.on_release
        )
        self.listener.start()
        self.listener.join()