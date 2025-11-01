"""
Виртуальная клавиатура с визуализацией нажатий клавиш
Рефакторинг с применением принципов ООП:
- Наследование
- Инкапсуляция
- Полиморфизм
- Фабричный паттерн
- Принцип единственной ответственности
"""

import tkinter as tk
from pynput import keyboard
import threading
import ctypes
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('virtual_keyboard.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============== КОНСТАНТЫ И КОНФИГУРАЦИЯ ==============
class Language(Enum):
    """Перечисление поддерживаемых языков"""
    ENGLISH = 'EN'
    RUSSIAN = 'RU'


class UIConfig:
    """Конфигурация UI элементов"""
    BG_COLOR = '#2b2b2b'
    BG_DARK = '#1a1a1a'
    FG_COLOR = '#ffffff'
    FG_HIGHLIGHT = '#00ff00'
    FG_BLACK = '#000000'

    KEY_DEFAULT_COLOR = '#404040'
    KEY_ACCENT_COLOR = '#5a5a5a'
    KEY_PRESSED_COLOR = '#00ff00'
    KEY_DIM_COLOR = '#408040'

    TITLE_COLOR_EN = '#4dabf7'
    TITLE_COLOR_RU = '#ff6b6b'

    FONT_FAMILY = 'Arial'
    FONT_FAMILY_MONO = 'Courier New'

    PADDING = 10
    SPACING = 5

    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 300
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 400


class KeyboardLayoutConfig:
    """Базовая конфигурация раскладки клавиатуры"""

    # Общая раскладка функциональных клавиш
    FUNCTION_ROW = ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']

    # Веса позиций для всех раскладок
    POSITION_WEIGHTS = {
        (0, 0): 5, (0, 1): 4, (0, 2): 4, (0, 3): 4, (0, 4): 4, (0, 5): 4,
        (0, 6): 4, (0, 7): 4, (0, 8): 4, (0, 9): 4, (0, 10): 4, (0, 11): 4, (0, 12): 4,
        (1, 0): 4, (1, 1): 4, (1, 2): 4, (1, 3): 4, (1, 4): 4, (1, 5): 4,
        (1, 6): 4, (1, 7): 4, (1, 8): 4, (1, 9): 4, (1, 10): 4, (1, 11): 4, (1, 12): 4, (1, 13): 10,
        (2, 0): 6, (2, 1): 4, (2, 2): 4, (2, 3): 4, (2, 4): 4, (2, 5): 4,
        (2, 6): 4, (2, 7): 4, (2, 8): 4, (2, 9): 4, (2, 10): 4, (2, 11): 4, (2, 12): 4, (2, 13): 4,
        (3, 0): 7, (3, 1): 4, (3, 2): 4, (3, 3): 4, (3, 4): 4, (3, 5): 4,
        (3, 6): 4, (3, 7): 4, (3, 8): 4, (3, 9): 4, (3, 10): 4, (3, 11): 4, (3, 12): 9,
        (4, 0): 8, (4, 1): 4, (4, 2): 4, (4, 3): 4, (4, 4): 4, (4, 5): 4,
        (4, 6): 4, (4, 7): 4, (4, 8): 4, (4, 9): 4, (4, 10): 4, (4, 11): 8,
        (5, 0): 5, (5, 1): 5, (5, 2): 5, (5, 3): 25, (5, 4): 5, (5, 5): 5, (5, 6): 5, (5, 7): 5,
    }

    # Общий маппинг специальных клавиш
    SPECIAL_KEY_MAPPING = {
        'esc': 'ESC',
        'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4',
        'f5': 'F5', 'f6': 'F6', 'f7': 'F7', 'f8': 'F8',
        'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12',
        'backspace': 'BACKSPACE',
        'tab': 'TAB',
        'caps_lock': 'CAPS',
        'enter': 'ENTER',
        'shift': 'SHIFT',
        'shift_r': 'SHIFT',
        'ctrl': 'CTRL',
        'ctrl_r': 'CTRL',
        'alt': 'ALT',
        'alt_r': 'ALT',
        'cmd': 'WIN',
        'cmd_r': 'WIN',
        'space': 'SPACE',
        'menu': 'MENU',
    }


class EnglishLayoutConfig(KeyboardLayoutConfig):
    """Конфигурация английской раскладки"""

    LAYOUT = [
        KeyboardLayoutConfig.FUNCTION_ROW,
        ['` | ~', '1 | !', '2 | @', '3 | #', '4 | $', '5 | %', '6 | ^', '7 | &', '8 | *', '9 | (', '0 | )', '- | _', '= | +', 'BACKSPACE'],
        ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[ | {', '] | }', '\\ | |'],
        ['CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '; | :', '\' | "', 'ENTER'],
        ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ', | <', '. | >', '/ | ?', 'SHIFT'],
        ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'WIN', 'MENU', 'CTRL']
    ]

    HOME_ROW_KEYS = ['F', 'J']


class RussianLayoutConfig(KeyboardLayoutConfig):
    """Конфигурация русской раскладки"""

    LAYOUT = [
        KeyboardLayoutConfig.FUNCTION_ROW,
        ['Ё | Ё', '1 | !', '2 | "', '3 | №', '4 | ;', '5 | %', '6 | :', '7 | ?', '8 | *', '9 | (', '0 | )', '- | _', '= | +', 'BACKSPACE'],
        ['TAB', 'Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ', '\\ | /'],
        ['CAPS', 'Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э', 'ENTER'],
        ['SHIFT', 'Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', '. | ,', 'SHIFT'],
        ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'WIN', 'MENU', 'CTRL']
    ]

    HOME_ROW_KEYS = ['А', 'О']

    # Маппинг английских символов на русские
    EN_TO_RU_MAP = {
        'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
        'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д',
        'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
        'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
        'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л', 'L': 'Д',
        'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т', 'M': 'Ь',
        '[': 'х', ']': 'ъ', ';': 'ж', "'": 'э', ',': 'б', '.': 'ю', '/': '.',
        '{': 'Х', '}': 'Ъ', ':': 'Ж', '"': 'Э', '<': 'Б', '>': 'Ю', '?': ',',
        '`': 'ё', '~': 'Ё'
    }


# ============== БАЗОВЫЙ КЛАСС ВИЗУАЛИЗАТОРА ==============
class BaseKeyboardVisualizer(ABC):
    """Абстрактный базовый класс для визуализации клавиатуры"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.buttons: Dict[str, List[tk.Label]] = {}
        self.button_widgets: List[tk.Label] = []
        self.button_colors: Dict[tk.Label, str] = {}
        self.button_positions: Dict[Tuple[int, int], tk.Label] = {}
        self.scale_factor = 1.0
        self.last_pressed_buttons: List[tk.Label] = []
        self.main_frame: Optional[tk.Frame] = None
        self.text_display: Optional[tk.Label] = None

    @abstractmethod
    def get_layout(self) -> List[List[str]]:
        """Возвращает раскладку клавиатуры"""
        pass

    @abstractmethod
    def get_home_row_keys(self) -> List[str]:
        """Возвращает клавиши домашней строки для выделения"""
        pass

    @abstractmethod
    def get_title(self) -> str:
        """Возвращает заголовок окна"""
        pass

    @abstractmethod
    def get_title_color(self) -> str:
        """Возвращает цвет заголовка"""
        pass

    def get_position_weights(self) -> Dict[Tuple[int, int], int]:
        """Возвращает веса позиций клавиш"""
        return KeyboardLayoutConfig.POSITION_WEIGHTS

    def create_keyboard(self, typed_text: str = ""):
        """Создание визуальной клавиатуры"""
        if self.main_frame is not None:
            self.main_frame.destroy()

        self._reset_internal_state()
        self._create_main_frame()
        self._create_title()
        self._create_text_display(typed_text)
        self._create_keyboard_layout()

    def _reset_internal_state(self):
        """Сброс внутреннего состояния"""
        self.buttons = {}
        self.button_widgets = []
        self.button_colors = {}
        self.button_positions = {}

    def _create_main_frame(self):
        """Создание главного фрейма"""
        self.main_frame = tk.Frame(self.root, bg=UIConfig.BG_COLOR,
                                   padx=UIConfig.PADDING, pady=UIConfig.PADDING)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=1)

    def _create_title(self):
        """Создание заголовка"""
        title_size = max(8, int(12 * self.scale_factor))
        title_label = tk.Label(
            self.main_frame,
            text=self.get_title(),
            bg=UIConfig.BG_COLOR,
            fg=self.get_title_color(),
            font=(UIConfig.FONT_FAMILY, title_size, 'bold'),
            pady=UIConfig.PADDING
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(0, UIConfig.PADDING))

    def _create_text_display(self, typed_text: str):
        """Создание текстового дисплея"""
        text_size = max(12, int(20 * self.scale_factor))
        self.text_display = tk.Label(
            self.main_frame,
            text=typed_text if typed_text else " ",
            bg=UIConfig.BG_DARK,
            fg=UIConfig.FG_HIGHLIGHT,
            font=(UIConfig.FONT_FAMILY_MONO, text_size, 'bold'),
            relief=tk.SUNKEN,
            borderwidth=2,
            anchor='center',
            padx=UIConfig.PADDING,
            pady=8,
            width=50
        )
        self.text_display.grid(row=1, column=0, sticky='ew', pady=(0, UIConfig.PADDING))

    def _create_keyboard_layout(self):
        """Создание раскладки клавиатуры"""
        keyboard_container = tk.Frame(self.main_frame, bg=UIConfig.BG_COLOR)
        keyboard_container.grid(row=2, column=0, sticky='nsew')
        self.main_frame.rowconfigure(2, weight=1)

        layout = self.get_layout()
        position_weights = self.get_position_weights()
        home_row_keys = self.get_home_row_keys()

        # Создаем список всех элементов без вложенных циклов
        layout_items = [(row_idx, col_idx, key)
                       for row_idx, row in enumerate(layout)
                       for col_idx, key in enumerate(row)]

        row_frames = {}

        # Обрабатываем все элементы
        for row_idx, col_idx, key in layout_items:
            # Создаем row_frame если еще не создан
            if row_idx not in row_frames:
                keyboard_container.rowconfigure(row_idx, weight=1)
                row_frame = tk.Frame(keyboard_container, bg=UIConfig.BG_COLOR)
                row_frame.grid(row=row_idx, column=0, sticky='nsew', pady=UIConfig.SPACING)
                row_frame.rowconfigure(0, weight=1)
                row_frames[row_idx] = row_frame
            else:
                row_frame = row_frames[row_idx]

            weight = position_weights.get((row_idx, col_idx), 4)
            row_frame.columnconfigure(col_idx, weight=weight)

            base_key = key.split('|')[0].strip() if '|' in key else key
            bg_color = (UIConfig.KEY_ACCENT_COLOR if base_key.upper() in home_row_keys
                       else UIConfig.KEY_DEFAULT_COLOR)

            button_size = max(6, int(10 * self.scale_factor))
            btn = tk.Label(
                row_frame,
                text=key,
                relief=tk.RAISED,
                bg=bg_color,
                fg=UIConfig.FG_COLOR,
                font=(UIConfig.FONT_FAMILY, button_size, 'bold'),
                borderwidth=2,
                width=1
            )
            btn.grid(row=0, column=col_idx, sticky='nsew', padx=UIConfig.SPACING, pady=0)

            # Регистрируем символы для кнопки
            self._register_button_symbols(key, btn)

            self.button_colors[btn] = bg_color
            self.button_widgets.append(btn)
            self.button_positions[(row_idx, col_idx)] = btn

        keyboard_container.columnconfigure(0, weight=1)

    def _register_button_symbols(self, key: str, btn: tk.Label):
        """Регистрация символов для кнопки"""
        symbols = [s.strip() for s in key.split('|')] if '|' in key else [key]
        for symbol in symbols:
            symbol_lower = symbol.lower()
            self.buttons.setdefault(symbol_lower, []).append(btn)
            symbol_upper = symbol.upper()
            if symbol_upper != symbol_lower:
                self.buttons.setdefault(symbol_upper, []).append(btn)

    def update_text_display(self, text: str):
        """Обновление текстового дисплея"""
        try:
            if self.text_display and self.text_display.winfo_exists():
                display_text = text if text else " "
                self.text_display.config(text=display_text)
        except:
            pass

    def highlight_key(self, key_name: str, key_mapping: Dict[str, str]):
        """Подсветка клавиши"""
        try:
            buttons_to_highlight = self._find_buttons_to_highlight(key_name, key_mapping)

            if buttons_to_highlight and buttons_to_highlight == self.last_pressed_buttons:
                self._reset_button_colors(self.last_pressed_buttons)
                self.last_pressed_buttons = []
                return

            self._reset_button_colors(self.last_pressed_buttons)
            self._set_button_colors(buttons_to_highlight, UIConfig.KEY_PRESSED_COLOR, UIConfig.FG_BLACK)

            self.root.after(200, lambda: self._set_dim_color(buttons_to_highlight))
            self.last_pressed_buttons = buttons_to_highlight
        except:
            pass

    def _find_buttons_to_highlight(self, key_name: str, key_mapping: Dict[str, str]) -> List[tk.Label]:
        """Поиск кнопок для подсветки"""
        key_lower = key_name.lower()
        key_upper = key_name.upper()

        if key_lower in self.buttons:
            return self.buttons[key_lower]
        elif key_upper in self.buttons:
            return self.buttons[key_upper]
        elif key_name in self.buttons:
            return self.buttons[key_name]

        # Поиск через маппинг
        for mapped_key, display_key in key_mapping.items():
            if mapped_key in key_lower or key_lower == mapped_key:
                display_lower = display_key.lower()
                if display_lower in self.buttons:
                    return self.buttons[display_lower]

        return []

    def _reset_button_colors(self, buttons: List[tk.Label]):
        """Сброс цветов кнопок"""
        for btn in buttons:
            if btn.winfo_exists():
                base_color = self.button_colors.get(btn, UIConfig.KEY_DEFAULT_COLOR)
                btn.configure(bg=base_color, fg=UIConfig.FG_COLOR)

    def _set_button_colors(self, buttons: List[tk.Label], bg_color: str, fg_color: str):
        """Установка цветов кнопок"""
        for btn in buttons:
            if btn.winfo_exists():
                btn.configure(bg=bg_color, fg=fg_color)

    def _set_dim_color(self, buttons: List[tk.Label]):
        """Установка приглушенного цвета"""
        for btn in buttons:
            if btn in self.last_pressed_buttons:
                try:
                    if btn.winfo_exists():
                        btn.configure(bg=UIConfig.KEY_DIM_COLOR, fg=UIConfig.FG_COLOR)
                except:
                    pass

    def reset_highlights(self):
        """Сброс всех подсветок"""
        try:
            self._reset_button_colors(self.last_pressed_buttons)
            self.last_pressed_buttons = []
        except:
            self.last_pressed_buttons = []


# ============== КОНКРЕТНЫЕ ВИЗУАЛИЗАТОРЫ ==============
class EnglishKeyboardVisualizer(BaseKeyboardVisualizer):
    """Визуализатор английской клавиатуры"""

    def get_layout(self) -> List[List[str]]:
        return EnglishLayoutConfig.LAYOUT

    def get_home_row_keys(self) -> List[str]:
        return EnglishLayoutConfig.HOME_ROW_KEYS

    def get_title(self) -> str:
        return "🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: EN"

    def get_title_color(self) -> str:
        return UIConfig.TITLE_COLOR_EN


class RussianKeyboardVisualizer(BaseKeyboardVisualizer):
    """Визуализатор русской клавиатуры"""

    def get_layout(self) -> List[List[str]]:
        return RussianLayoutConfig.LAYOUT

    def get_home_row_keys(self) -> List[str]:
        return RussianLayoutConfig.HOME_ROW_KEYS

    def get_title(self) -> str:
        return "🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: RU"

    def get_title_color(self) -> str:
        return UIConfig.TITLE_COLOR_RU


# ============== БАЗОВЫЙ КЛАСС КОНТРОЛЛЕРА ==============
class BaseKeyboardController(ABC):
    """Абстрактный базовый класс для управления клавиатурой"""

    def __init__(self, visualizer: BaseKeyboardVisualizer):
        self.visualizer = visualizer
        self.typed_text = ""
        self.max_text_length = 50
        self.caps_lock_on = False
        self.shift_pressed = False
        self.key_mapping = KeyboardLayoutConfig.SPECIAL_KEY_MAPPING.copy()

    @abstractmethod
    def process_character(self, char: str) -> str:
        """Обработка символа с учетом языка"""
        pass

    def add_character(self, char: str):
        """Добавление символа в текст"""
        if char is not None:
            logger.debug(f"[{self.__class__.__name__}] add_character: input='{char}', "
                        f"caps_lock={self.caps_lock_on}, shift={self.shift_pressed}")

            processed_char = self.process_character(char)
            self.typed_text += processed_char

            if len(self.typed_text) > self.max_text_length:
                self.typed_text = self.typed_text[-self.max_text_length:]

            logger.debug(f"[{self.__class__.__name__}] add_character: output='{processed_char}', "
                        f"typed_text='{self.typed_text}'")
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
            self.caps_lock_on = not self.caps_lock_on

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


# ============== КОНКРЕТНЫЕ КОНТРОЛЛЕРЫ ==============
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
                logger.debug(f"[RU] Ignored duplicate key_char='{key_char}', time_diff={time_diff:.3f}")
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


# ============== ФАБРИКА РАСКЛАДОК ==============
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


# ============== СЕРВИС ОПРЕДЕЛЕНИЯ ЯЗЫКА ==============
class LanguageDetector:
    """Сервис для определения языка клавиатуры"""

    @staticmethod
    def get_current_language() -> Language:
        """Определение текущего языка клавиатуры в Windows"""
        try:
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            curr_window = user32.GetForegroundWindow()
            thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
            klid = user32.GetKeyboardLayout(thread_id)
            lid = klid & 0xFFFF

            if lid == 0x0419:
                return Language.RUSSIAN
            else:
                return Language.ENGLISH
        except Exception:
            return Language.ENGLISH


# ============== МЕНЕДЖЕР РАСКЛАДОК ==============
class LayoutManager:
    """Менеджер для переключения между раскладками"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_language = Language.ENGLISH
        self.layouts: Dict[Language, Tuple[BaseKeyboardVisualizer, BaseKeyboardController]] = {}
        self.current_visualizer: Optional[BaseKeyboardVisualizer] = None
        self.current_controller: Optional[BaseKeyboardController] = None
        self.listener: Optional[keyboard.Listener] = None

        logger.info("LayoutManager: Инициализация")
        self._initialize_layouts()
        self._start_monitoring()

    def _initialize_layouts(self):
        """Инициализация всех раскладок"""
        for lang in Language:
            visualizer, controller = KeyboardFactory.create_layout(lang, self.root)
            self.layouts[lang] = (visualizer, controller)

        # Устанавливаем текущую раскладку
        self.current_visualizer, self.current_controller = self.layouts[self.current_language]
        logger.info("LayoutManager: Раскладки инициализированы")

    def _start_monitoring(self):
        """Запуск мониторинга раскладки и слушателя клавиатуры"""
        layout_monitor_thread = threading.Thread(target=self._monitor_layout, daemon=True)
        layout_monitor_thread.start()

        listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        listener_thread.start()

        logger.info("LayoutManager: Мониторинг и слушатель запущены")

    def _monitor_layout(self):
        """Мониторинг изменения раскладки клавиатуры"""
        while True:
            try:
                new_language = LanguageDetector.get_current_language()
                if new_language != self.current_language:
                    logger.info(f"LayoutManager: Обнаружено изменение раскладки: "
                              f"{self.current_language} -> {new_language}")
                    self.current_language = new_language
                    self.root.after(0, self.switch_layout)
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"LayoutManager: Ошибка в _monitor_layout: {e}")
                time.sleep(0.1)

    def switch_layout(self):
        """Переключение раскладки"""
        logger.info(f"LayoutManager: Начало переключения на раскладку {self.current_language}")

        # Сохраняем текущий текст
        current_text = self.current_controller.get_typed_text()
        logger.debug(f"LayoutManager: Сохранен текст: '{current_text}'")

        # Останавливаем текущий слушатель
        if self.listener:
            self.listener.stop()
            logger.debug("LayoutManager: Слушатель остановлен")

        # Удаляем main_frame текущего визуализатора
        if self.current_visualizer.main_frame is not None:
            self.current_visualizer.main_frame.destroy()
            self.current_visualizer.main_frame = None
            logger.debug("LayoutManager: Старый main_frame удален")

        # Переключаем на новую раскладку
        self.current_visualizer, self.current_controller = self.layouts[self.current_language]
        logger.info(f"LayoutManager: Переключено на {self.current_language.value} раскладку")

        # Передаем сохраненный текст в новый контроллер
        self.current_controller.set_typed_text(current_text)
        logger.debug("LayoutManager: Текст передан новому контроллеру")

        # Создаем клавиатуру с сохраненным текстом
        self.current_visualizer.create_keyboard(current_text)
        logger.debug("LayoutManager: Клавиатура создана")

        # Перезапускаем слушатель с новым контроллером
        self.listener = keyboard.Listener(
            on_press=self.current_controller.on_press,
            on_release=self.current_controller.on_release
        )
        self.listener.start()
        logger.info("LayoutManager: Новый слушатель запущен, переключение завершено")

    def _start_listener(self):
        """Запуск первого слушателя клавиатуры"""
        time.sleep(0.5)  # Даем время на инициализацию
        self.listener = keyboard.Listener(
            on_press=self.current_controller.on_press,
            on_release=self.current_controller.on_release
        )
        self.listener.start()
        self.listener.join()


# ============== ГЛАВНОЕ ПРИЛОЖЕНИЕ ==============
class VirtualKeyboardApp:
    """Главное приложение виртуальной клавиатуры"""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("ЗАПУСК ВИРТУАЛЬНОЙ КЛАВИАТУРЫ")
        logger.info("=" * 80)

        self.root = self._create_window()
        self.manager = LayoutManager(self.root)
        self.manager.current_visualizer.create_keyboard()

        logger.info("Начальная клавиатура создана")

    def _create_window(self) -> tk.Tk:
        """Создание главного окна"""
        root = tk.Tk()
        root.title("Виртуальная клавиатура")
        root.configure(bg=UIConfig.BG_COLOR)
        root.attributes('-topmost', True)
        root.resizable(True, True)
        root.minsize(UIConfig.MIN_WINDOW_WIDTH, UIConfig.MIN_WINDOW_HEIGHT)
        root.geometry(f"{UIConfig.DEFAULT_WINDOW_WIDTH}x{UIConfig.DEFAULT_WINDOW_HEIGHT}")
        logger.info("Главное окно создано")
        return root

    def run(self):
        """Запуск приложения"""
        logger.info("Запуск главного цикла")
        self.root.mainloop()
        logger.info("Программа завершена")


if __name__ == '__main__':
    app = VirtualKeyboardApp()
    app.run()