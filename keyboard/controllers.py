"""
Модуль контроллеров клавиатуры
Содержит базовый класс и конкретные реализации для управления вводом
"""

import time
from abc import ABC, abstractmethod
from typing import Dict

from .visualizers import BaseKeyboardVisualizer
from .config import KeyboardLayoutConfig, RussianLayoutConfig
from .services import CapsLockDetector


class BaseKeyboardController(ABC):
    """Абстрактный базовый класс для управления клавиатурой"""

    def __init__(self, visualizer: BaseKeyboardVisualizer):
        self.visualizer = visualizer
        self.typed_text = ""
        self.max_text_length = 50
        # Синхронизируем с системным состоянием Caps Lock
        self.caps_lock_on = CapsLockDetector.is_caps_lock_on()
        self.shift_pressed = False
        self.key_mapping = KeyboardLayoutConfig.SPECIAL_KEY_MAPPING.copy()

    @abstractmethod
    def process_character(self, char: str) -> str:
        """Обработка символа с учетом языка"""
        pass

    def add_character(self, char: str):
        """Добавление символа в текст"""
        if char is not None:
            processed_char = self.process_character(char)
            self.typed_text += processed_char

            if len(self.typed_text) > self.max_text_length:
                self.typed_text = self.typed_text[-self.max_text_length:]

            self.visualizer.update_text_display(self.typed_text)

    def handle_special_key(self, key_name: str):
        """Обработка специальных клавиш"""
        if key_name == 'backspace':
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
                self.visualizer.update_text_display(self.typed_text)
        elif key_name == 'space':
            self.add_character(' ')
        elif key_name == 'enter':
            self.typed_text = ""
            self.visualizer.update_text_display(self.typed_text)
        elif key_name == 'esc':
            self.typed_text = ""
            self.visualizer.update_text_display(self.typed_text)
        elif key_name == 'caps_lock':
            # Синхронизируемся с системным состоянием вместо простого переключения
            self.caps_lock_on = CapsLockDetector.is_caps_lock_on()

    def on_press(self, key):
        """Обработка нажатия клавиши"""
        try:
            key_char = key.char
            self._handle_character_key(key_char)
        except AttributeError:
            key_name = str(key).replace('Key.', '')
            self._handle_special_key_press(key_name)

    def on_release(self, key):
        """Обработка отпускания клавиши"""
        try:
            key_name = str(key).replace('Key.', '')
            if key_name in ['shift', 'shift_r']:
                self.shift_pressed = False
        except AttributeError:
            pass

    @abstractmethod
    def _handle_character_key(self, key_char: str):
        """Обработка символьной клавиши"""
        pass

    def _handle_special_key_press(self, key_name: str):
        """Обработка нажатия специальной клавиши"""
        if key_name in ['shift', 'shift_r']:
            self.shift_pressed = True
        self.visualizer.root.after(0, lambda: self.visualizer.highlight_key(key_name, self.key_mapping))
        self.visualizer.root.after(0, lambda: self.handle_special_key(key_name))

    def get_typed_text(self) -> str:
        """Получение набранного текста"""
        return self.typed_text

    def set_typed_text(self, text: str):
        """Установка набранного текста"""
        self.typed_text = text
        if self.visualizer and self.visualizer.text_display:
            try:
                self.visualizer.update_text_display(self.typed_text)
            except:
                pass

    def sync_caps_lock_state(self):
        """Синхронизация состояния Caps Lock с системным"""
        self.caps_lock_on = CapsLockDetector.is_caps_lock_on()


class EnglishKeyboardController(BaseKeyboardController):
    """Контроллер английской клавиатуры"""

    def process_character(self, char: str) -> str:
        """Обработка английского символа"""
        if char.isalpha():
            if self.caps_lock_on != self.shift_pressed:
                return char.upper()
            else:
                return char.lower()
        return char

    def _handle_character_key(self, key_char: str):
        """Обработка символьной клавиши"""
        self.visualizer.root.after(0, lambda: self.visualizer.highlight_key(key_char, self.key_mapping))
        self.visualizer.root.after(0, lambda: self.add_character(key_char))


class RussianKeyboardController(BaseKeyboardController):
    """Контроллер русской клавиатуры"""

    def __init__(self, visualizer: BaseKeyboardVisualizer):
        super().__init__(visualizer)
        self.last_key_time: Dict[str, float] = {}
        self.en_to_ru_map = RussianLayoutConfig.EN_TO_RU_MAP

    def process_character(self, char: str) -> str:
        """Обработка русского символа (конвертация из английского)"""
        # Применяем Caps Lock и Shift к английскому символу
        if char.isalpha():
            if self.caps_lock_on != self.shift_pressed:
                char = char.upper()
            else:
                char = char.lower()

        # Конвертируем в русский
        if char in self.en_to_ru_map:
            return self.en_to_ru_map[char]
        return char

    def _handle_character_key(self, key_char: str):
        """Обработка символьной клавиши с защитой от дублирования"""
        current_time = time.time()
        if key_char in self.last_key_time:
            time_diff = current_time - self.last_key_time[key_char]
            if time_diff < 0.05:
                return

        self.last_key_time[key_char] = current_time

        # Для подсветки нужно конвертировать английский символ в русский
        highlight_char = key_char
        if key_char.isalpha():
            if self.caps_lock_on != self.shift_pressed:
                highlight_char = key_char.upper()
            else:
                highlight_char = key_char.lower()

        if highlight_char in self.en_to_ru_map:
            highlight_char = self.en_to_ru_map[highlight_char]

        # Используем closure для захвата значений
        def do_highlight(hc=highlight_char):
            self.visualizer.highlight_key(hc, self.key_mapping)

        def do_add(kc=key_char):
            self.add_character(kc)

        self.visualizer.root.after(0, do_highlight)
        self.visualizer.root.after(0, do_add)