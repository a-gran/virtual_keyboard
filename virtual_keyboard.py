"""
Виртуальная клавиатура с визуализацией нажатий клавиш
Клавиши подсвечиваются при нажатии
Отдельные классы для английской и русской раскладки
"""

import tkinter as tk
from pynput import keyboard
import threading
import ctypes
import time
import logging

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


# ============== ВИЗУАЛИЗАЦИЯ ДЛЯ АНГЛИЙСКОЙ РАСКЛАДКИ ==============
class EnglishKeyboardVisualizer:
    """Класс для визуализации английской клавиатуры"""

    def __init__(self, root):
        self.root = root
        self.buttons = {}
        self.button_widgets = []
        self.button_colors = {}
        self.button_positions = {}
        self.scale_factor = 1.0
        self.last_pressed_buttons = []
        self.main_frame = None
        self.text_display = None

        # Английская раскладка клавиатуры
        self.keyboard_layout = [
            ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['` | ~', '1 | !', '2 | @', '3 | #', '4 | $', '5 | %', '6 | ^', '7 | &', '8 | *', '9 | (', '0 | )', '- | _', '= | +', 'BACKSPACE'],
            ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[ | {', '] | }', '\\ | |'],
            ['CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '; | :', '\' | "', 'ENTER'],
            ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ', | <', '. | >', '/ | ?', 'SHIFT'],
            ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'WIN', 'MENU', 'CTRL']
        ]

        self.position_weights = {
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

    def create_keyboard(self, typed_text=""):
        """Создание визуальной клавиатуры"""
        if self.main_frame is not None:
            self.main_frame.destroy()

        self.buttons = {}
        self.button_widgets = []
        self.button_colors = {}
        self.button_positions = {}

        self.main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=1)

        # Заголовок
        title_size = max(8, int(12 * self.scale_factor))
        title_label = tk.Label(
            self.main_frame,
            text="🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: EN",
            bg='#2b2b2b',
            fg='#4dabf7',
            font=('Arial', title_size, 'bold'),
            pady=10
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        # Текстовое поле
        text_size = max(12, int(20 * self.scale_factor))
        self.text_display = tk.Label(
            self.main_frame,
            text=typed_text if typed_text else " ",
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier New', text_size, 'bold'),
            relief=tk.SUNKEN,
            borderwidth=2,
            anchor='center',
            padx=10,
            pady=8,
            width=50
        )
        self.text_display.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        # Контейнер для клавиатуры
        keyboard_container = tk.Frame(self.main_frame, bg='#2b2b2b')
        keyboard_container.grid(row=2, column=0, sticky='nsew')
        self.main_frame.rowconfigure(2, weight=1)

        # Создание рядов клавиш
        for row_idx, row in enumerate(self.keyboard_layout):
            keyboard_container.rowconfigure(row_idx, weight=1)
            row_frame = tk.Frame(keyboard_container, bg='#2b2b2b')
            row_frame.grid(row=row_idx, column=0, sticky='nsew', pady=5)
            row_frame.rowconfigure(0, weight=1)

            for col_idx, key in enumerate(row):
                weight = self.position_weights.get((row_idx, col_idx), 4)
                row_frame.columnconfigure(col_idx, weight=weight)

                base_key = key.split('|')[0].strip() if '|' in key else key
                if base_key.upper() in ['F', 'J']:
                    bg_color = '#5a5a5a'
                else:
                    bg_color = '#404040'

                button_size = max(6, int(10 * self.scale_factor))
                btn = tk.Label(
                    row_frame,
                    text=key,
                    relief=tk.RAISED,
                    bg=bg_color,
                    fg='#ffffff',
                    font=('Arial', button_size, 'bold'),
                    borderwidth=2,
                    width=1
                )
                btn.grid(row=0, column=col_idx, sticky='nsew', padx=5, pady=0)

                if '|' in key:
                    symbols = [s.strip() for s in key.split('|')]
                    for symbol in symbols:
                        symbol_lower = symbol.lower()
                        if symbol_lower not in self.buttons:
                            self.buttons[symbol_lower] = []
                        self.buttons[symbol_lower].append(btn)
                        symbol_upper = symbol.upper()
                        if symbol_upper != symbol_lower:
                            if symbol_upper not in self.buttons:
                                self.buttons[symbol_upper] = []
                            self.buttons[symbol_upper].append(btn)
                else:
                    key_lower = key.lower()
                    if key_lower not in self.buttons:
                        self.buttons[key_lower] = []
                    self.buttons[key_lower].append(btn)
                    key_upper = key.upper()
                    if key_upper != key_lower:
                        if key_upper not in self.buttons:
                            self.buttons[key_upper] = []
                        self.buttons[key_upper].append(btn)

                self.button_colors[btn] = bg_color
                self.button_widgets.append(btn)
                self.button_positions[(row_idx, col_idx)] = btn

        keyboard_container.columnconfigure(0, weight=1)

    def update_text_display(self, text):
        try:
            if self.text_display and self.text_display.winfo_exists():
                display_text = text if text else " "
                self.text_display.config(text=display_text)
        except:
            pass

    def highlight_key(self, key_name, key_mapping):
        try:
            key_lower = key_name.lower()
            key_upper = key_name.upper()
            buttons_to_highlight = []

            if key_lower in self.buttons:
                buttons_to_highlight = self.buttons[key_lower]
            elif key_upper in self.buttons:
                buttons_to_highlight = self.buttons[key_upper]
            elif key_name in self.buttons:
                buttons_to_highlight = self.buttons[key_name]

            if not buttons_to_highlight:
                for mapped_key, display_key in key_mapping.items():
                    if mapped_key in key_lower or key_lower == mapped_key:
                        display_lower = display_key.lower()
                        if display_lower in self.buttons:
                            buttons_to_highlight = self.buttons[display_lower]
                            break

            if buttons_to_highlight and buttons_to_highlight == self.last_pressed_buttons:
                for btn in self.last_pressed_buttons:
                    if btn.winfo_exists():
                        base_color = self.button_colors.get(btn, '#404040')
                        btn.configure(bg=base_color, fg='#ffffff')
                self.last_pressed_buttons = []
                return

            for btn in self.last_pressed_buttons:
                if btn.winfo_exists():
                    base_color = self.button_colors.get(btn, '#404040')
                    btn.configure(bg=base_color, fg='#ffffff')

            for btn in buttons_to_highlight:
                if btn.winfo_exists():
                    btn.configure(bg='#00ff00', fg='#000000')

            def set_dim_color():
                for btn in buttons_to_highlight:
                    if btn in self.last_pressed_buttons:
                        try:
                            if btn.winfo_exists():
                                btn.configure(bg='#408040', fg='#ffffff')
                        except:
                            pass

            self.root.after(200, set_dim_color)
            self.last_pressed_buttons = buttons_to_highlight
        except:
            pass

    def reset_highlights(self):
        try:
            for btn in self.last_pressed_buttons:
                if btn.winfo_exists():
                    base_color = self.button_colors.get(btn, '#404040')
                    btn.configure(bg=base_color, fg='#ffffff')
            self.last_pressed_buttons = []
        except:
            self.last_pressed_buttons = []


# ============== ВИЗУАЛИЗАЦИЯ ДЛЯ РУССКОЙ РАСКЛАДКИ ==============
class RussianKeyboardVisualizer:
    """Класс для визуализации русской клавиатуры"""

    def __init__(self, root):
        self.root = root
        self.buttons = {}
        self.button_widgets = []
        self.button_colors = {}
        self.button_positions = {}
        self.scale_factor = 1.0
        self.last_pressed_buttons = []
        self.main_frame = None
        self.text_display = None

        # Русская раскладка клавиатуры
        self.keyboard_layout = [
            ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['Ё | Ё', '1 | !', '2 | "', '3 | №', '4 | ;', '5 | %', '6 | :', '7 | ?', '8 | *', '9 | (', '0 | )', '- | _', '= | +', 'BACKSPACE'],
            ['TAB', 'Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ', '\\ | /'],
            ['CAPS', 'Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э', 'ENTER'],
            ['SHIFT', 'Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', '. | ,', 'SHIFT'],
            ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'WIN', 'MENU', 'CTRL']
        ]

        self.position_weights = {
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

    def create_keyboard(self, typed_text=""):
        """Создание визуальной клавиатуры"""
        if self.main_frame is not None:
            self.main_frame.destroy()

        self.buttons = {}
        self.button_widgets = []
        self.button_colors = {}
        self.button_positions = {}

        self.main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=1)

        # Заголовок
        title_size = max(8, int(12 * self.scale_factor))
        title_label = tk.Label(
            self.main_frame,
            text="🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: RU",
            bg='#2b2b2b',
            fg='#ff6b6b',
            font=('Arial', title_size, 'bold'),
            pady=10
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        # Текстовое поле
        text_size = max(12, int(20 * self.scale_factor))
        self.text_display = tk.Label(
            self.main_frame,
            text=typed_text if typed_text else " ",
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier New', text_size, 'bold'),
            relief=tk.SUNKEN,
            borderwidth=2,
            anchor='center',
            padx=10,
            pady=8,
            width=50
        )
        self.text_display.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        # Контейнер для клавиатуры
        keyboard_container = tk.Frame(self.main_frame, bg='#2b2b2b')
        keyboard_container.grid(row=2, column=0, sticky='nsew')
        self.main_frame.rowconfigure(2, weight=1)

        # Создание рядов клавиш
        for row_idx, row in enumerate(self.keyboard_layout):
            keyboard_container.rowconfigure(row_idx, weight=1)
            row_frame = tk.Frame(keyboard_container, bg='#2b2b2b')
            row_frame.grid(row=row_idx, column=0, sticky='nsew', pady=5)
            row_frame.rowconfigure(0, weight=1)

            for col_idx, key in enumerate(row):
                weight = self.position_weights.get((row_idx, col_idx), 4)
                row_frame.columnconfigure(col_idx, weight=weight)

                base_key = key.split('|')[0].strip() if '|' in key else key
                if base_key.upper() in ['А', 'О']:
                    bg_color = '#5a5a5a'
                else:
                    bg_color = '#404040'

                button_size = max(6, int(10 * self.scale_factor))
                btn = tk.Label(
                    row_frame,
                    text=key,
                    relief=tk.RAISED,
                    bg=bg_color,
                    fg='#ffffff',
                    font=('Arial', button_size, 'bold'),
                    borderwidth=2,
                    width=1
                )
                btn.grid(row=0, column=col_idx, sticky='nsew', padx=5, pady=0)

                if '|' in key:
                    symbols = [s.strip() for s in key.split('|')]
                    for symbol in symbols:
                        symbol_lower = symbol.lower()
                        if symbol_lower not in self.buttons:
                            self.buttons[symbol_lower] = []
                        self.buttons[symbol_lower].append(btn)
                        symbol_upper = symbol.upper()
                        if symbol_upper != symbol_lower:
                            if symbol_upper not in self.buttons:
                                self.buttons[symbol_upper] = []
                            self.buttons[symbol_upper].append(btn)
                else:
                    key_lower = key.lower()
                    if key_lower not in self.buttons:
                        self.buttons[key_lower] = []
                    self.buttons[key_lower].append(btn)
                    key_upper = key.upper()
                    if key_upper != key_lower:
                        if key_upper not in self.buttons:
                            self.buttons[key_upper] = []
                        self.buttons[key_upper].append(btn)

                self.button_colors[btn] = bg_color
                self.button_widgets.append(btn)
                self.button_positions[(row_idx, col_idx)] = btn

        keyboard_container.columnconfigure(0, weight=1)

    def update_text_display(self, text):
        try:
            if self.text_display and self.text_display.winfo_exists():
                display_text = text if text else " "
                self.text_display.config(text=display_text)
        except:
            pass

    def highlight_key(self, key_name, key_mapping):
        try:
            key_lower = key_name.lower()
            key_upper = key_name.upper()
            buttons_to_highlight = []

            if key_lower in self.buttons:
                buttons_to_highlight = self.buttons[key_lower]
            elif key_upper in self.buttons:
                buttons_to_highlight = self.buttons[key_upper]
            elif key_name in self.buttons:
                buttons_to_highlight = self.buttons[key_name]

            if not buttons_to_highlight:
                for mapped_key, display_key in key_mapping.items():
                    if mapped_key in key_lower or key_lower == mapped_key:
                        display_lower = display_key.lower()
                        if display_lower in self.buttons:
                            buttons_to_highlight = self.buttons[display_lower]
                            break

            if buttons_to_highlight and buttons_to_highlight == self.last_pressed_buttons:
                for btn in self.last_pressed_buttons:
                    if btn.winfo_exists():
                        base_color = self.button_colors.get(btn, '#404040')
                        btn.configure(bg=base_color, fg='#ffffff')
                self.last_pressed_buttons = []
                return

            for btn in self.last_pressed_buttons:
                if btn.winfo_exists():
                    base_color = self.button_colors.get(btn, '#404040')
                    btn.configure(bg=base_color, fg='#ffffff')

            for btn in buttons_to_highlight:
                if btn.winfo_exists():
                    btn.configure(bg='#00ff00', fg='#000000')

            def set_dim_color():
                for btn in buttons_to_highlight:
                    if btn in self.last_pressed_buttons:
                        try:
                            if btn.winfo_exists():
                                btn.configure(bg='#408040', fg='#ffffff')
                        except:
                            pass

            self.root.after(200, set_dim_color)
            self.last_pressed_buttons = buttons_to_highlight
        except:
            pass

    def reset_highlights(self):
        try:
            for btn in self.last_pressed_buttons:
                if btn.winfo_exists():
                    base_color = self.button_colors.get(btn, '#404040')
                    btn.configure(bg=base_color, fg='#ffffff')
            self.last_pressed_buttons = []
        except:
            self.last_pressed_buttons = []


# ============== ФУНКЦИОНАЛ ДЛЯ АНГЛИЙСКОЙ РАСКЛАДКИ ==============
class EnglishKeyboardController:
    """Класс для управления функциональностью английской клавиатуры"""

    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.typed_text = ""
        self.max_text_length = 50
        self.caps_lock_on = False
        self.shift_pressed = False

        self.key_mapping = {
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

    def add_character(self, char):
        """Добавление английского символа"""
        if char is not None:
            logger.debug(f"[EN] add_character: input='{char}', caps_lock={self.caps_lock_on}, shift={self.shift_pressed}")
            # Применяем Caps Lock и Shift ТОЛЬКО для английских букв
            if char.isalpha():
                if self.caps_lock_on != self.shift_pressed:
                    char = char.upper()
                else:
                    char = char.lower()

            self.typed_text += char
            if len(self.typed_text) > self.max_text_length:
                self.typed_text = self.typed_text[-self.max_text_length:]
            logger.debug(f"[EN] add_character: output='{char}', typed_text='{self.typed_text}'")
            self.visualizer.update_text_display(self.typed_text)

    def handle_special_key(self, key_name):
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
            self.visualizer.root.after(0, lambda: self.visualizer.highlight_key(key_char, self.key_mapping))
            self.visualizer.root.after(0, lambda: self.add_character(key_char))
        except AttributeError:
            key_name = str(key).replace('Key.', '')
            if key_name in ['shift', 'shift_r']:
                self.shift_pressed = True
            self.visualizer.root.after(0, lambda: self.visualizer.highlight_key(key_name, self.key_mapping))
            self.visualizer.root.after(0, lambda: self.handle_special_key(key_name))

    def on_release(self, key):
        """Обработка отпускания клавиши"""
        try:
            key_name = str(key).replace('Key.', '')
            if key_name in ['shift', 'shift_r']:
                self.shift_pressed = False
        except AttributeError:
            pass

    def get_typed_text(self):
        return self.typed_text

    def set_typed_text(self, text):
        self.typed_text = text
        # Обновляем только если visualizer и text_display существуют
        if self.visualizer and self.visualizer.text_display:
            try:
                self.visualizer.update_text_display(self.typed_text)
            except:
                pass


# ============== ФУНКЦИОНАЛ ДЛЯ РУССКОЙ РАСКЛАДКИ ==============
class RussianKeyboardController:
    """Класс для управления функциональностью русской клавиатуры"""

    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.typed_text = ""
        self.max_text_length = 50
        self.caps_lock_on = False
        self.shift_pressed = False
        self.last_key_time = {}  # Защита от дублирования нажатий

        self.key_mapping = {
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

        # Маппинг английских символов на русские (pynput возвращает английские!)
        # Используется БЕЗ учета регистра - регистр применяется позже
        self.en_to_ru_map = {
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

    def add_character(self, char):
        """Добавление русского символа (конвертируем из английского)"""
        if char is not None:
            original_char = char
            logger.debug(f"[RU] add_character: input='{char}', caps_lock={self.caps_lock_on}, shift={self.shift_pressed}")
            # Сначала применяем Caps Lock и Shift к английскому символу
            if char.isalpha():
                if self.caps_lock_on != self.shift_pressed:
                    char = char.upper()
                else:
                    char = char.lower()

            # ЗАТЕМ конвертируем английский символ в русский
            if char in self.en_to_ru_map:
                char = self.en_to_ru_map[char]
                logger.debug(f"[RU] Converted '{original_char}' -> '{char}'")

            self.typed_text += char
            if len(self.typed_text) > self.max_text_length:
                self.typed_text = self.typed_text[-self.max_text_length:]
            logger.debug(f"[RU] add_character: output='{char}', typed_text='{self.typed_text}'")
            self.visualizer.update_text_display(self.typed_text)

    def handle_special_key(self, key_name):
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

            # Защита от дублирования: проверяем время последнего нажатия этой клавиши
            current_time = time.time()
            if key_char in self.last_key_time:
                time_diff = current_time - self.last_key_time[key_char]
                if time_diff < 0.05:  # Игнорируем если прошло менее 50ms
                    logger.debug(f"[RU] on_press: IGNORED duplicate key_char='{key_char}', time_diff={time_diff:.3f}")
                    return

            self.last_key_time[key_char] = current_time
            logger.debug(f"[RU] on_press: key_char='{key_char}'")

            # Для подсветки нужно конвертировать английский символ в русский
            # Применяем Caps Lock и Shift к английскому символу для получения правильного регистра
            highlight_char = key_char
            if key_char.isalpha():
                if self.caps_lock_on != self.shift_pressed:
                    highlight_char = key_char.upper()
                else:
                    highlight_char = key_char.lower()

            # Конвертируем в русский для подсветки
            if highlight_char in self.en_to_ru_map:
                highlight_char = self.en_to_ru_map[highlight_char]

            logger.debug(f"[RU] on_press: highlight_char='{highlight_char}'")

            # Используем closure для захвата значений
            def do_highlight(hc=highlight_char):
                self.visualizer.highlight_key(hc, self.key_mapping)

            def do_add(kc=key_char):
                self.add_character(kc)

            self.visualizer.root.after(0, do_highlight)
            self.visualizer.root.after(0, do_add)
        except AttributeError:
            key_name = str(key).replace('Key.', '')
            if key_name in ['shift', 'shift_r']:
                self.shift_pressed = True

            def do_highlight_special(kn=key_name):
                self.visualizer.highlight_key(kn, self.key_mapping)

            def do_handle_special(kn=key_name):
                self.handle_special_key(kn)

            self.visualizer.root.after(0, do_highlight_special)
            self.visualizer.root.after(0, do_handle_special)

    def on_release(self, key):
        """Обработка отпускания клавиши"""
        try:
            key_name = str(key).replace('Key.', '')
            if key_name in ['shift', 'shift_r']:
                self.shift_pressed = False
        except AttributeError:
            pass

    def get_typed_text(self):
        return self.typed_text

    def set_typed_text(self, text):
        self.typed_text = text
        # Обновляем только если visualizer и text_display существуют
        if self.visualizer and self.visualizer.text_display:
            try:
                self.visualizer.update_text_display(self.typed_text)
            except:
                pass


# ============== МЕНЕДЖЕР РАСКЛАДОК ==============
class LayoutManager:
    """Менеджер для переключения между раскладками"""

    def __init__(self, root):
        self.root = root
        self.current_language = 'EN'
        logger.info("LayoutManager: Инициализация")

        # Создаем визуализаторы для обеих раскладок
        self.en_visualizer = EnglishKeyboardVisualizer(root)
        self.ru_visualizer = RussianKeyboardVisualizer(root)
        logger.info("LayoutManager: Визуализаторы созданы")

        # Создаем контроллеры для обеих раскладок
        self.en_controller = EnglishKeyboardController(self.en_visualizer)
        self.ru_controller = RussianKeyboardController(self.ru_visualizer)
        logger.info("LayoutManager: Контроллеры созданы")

        # Текущий активный контроллер
        self.current_controller = self.en_controller
        self.current_visualizer = self.en_visualizer

        # Слушатель клавиатуры
        self.listener = None

        # Запуск мониторинга раскладки
        self.layout_monitor_thread = threading.Thread(target=self.monitor_layout, daemon=True)
        self.layout_monitor_thread.start()
        logger.info("LayoutManager: Мониторинг раскладки запущен")

        # Запуск слушателя клавиатуры
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()
        logger.info("LayoutManager: Слушатель клавиатуры запущен")

    def get_keyboard_language(self):
        """Определение текущего языка клавиатуры в Windows"""
        try:
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            curr_window = user32.GetForegroundWindow()
            thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
            klid = user32.GetKeyboardLayout(thread_id)
            lid = klid & 0xFFFF

            if lid == 0x0419:
                return 'RU'
            else:
                return 'EN'
        except Exception:
            return 'EN'

    def monitor_layout(self):
        """Мониторинг изменения раскладки клавиатуры"""
        while True:
            try:
                new_language = self.get_keyboard_language()
                if new_language != self.current_language:
                    logger.info(f"LayoutManager: Обнаружено изменение раскладки: {self.current_language} -> {new_language}")
                    self.current_language = new_language
                    self.root.after(0, self.switch_layout)
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"LayoutManager: Ошибка в monitor_layout: {e}")
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

        # УДАЛЯЕМ main_frame текущего визуализатора перед переключением
        if self.current_visualizer.main_frame is not None:
            self.current_visualizer.main_frame.destroy()
            self.current_visualizer.main_frame = None
            logger.debug("LayoutManager: Старый main_frame удален")

        # Переключаем на нужную раскладку
        if self.current_language == 'EN':
            self.current_visualizer = self.en_visualizer
            self.current_controller = self.en_controller
            logger.info("LayoutManager: Переключено на английскую раскладку")
        else:
            self.current_visualizer = self.ru_visualizer
            self.current_controller = self.ru_controller
            logger.info("LayoutManager: Переключено на русскую раскладку")

        # Передаем сохраненный текст в новый контроллер
        self.current_controller.set_typed_text(current_text)
        logger.debug(f"LayoutManager: Текст передан новому контроллеру")

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

    def start_listener(self):
        """Запуск первого слушателя клавиатуры"""
        time.sleep(0.5)  # Даем время на инициализацию
        self.listener = keyboard.Listener(
            on_press=self.current_controller.on_press,
            on_release=self.current_controller.on_release
        )
        self.listener.start()
        self.listener.join()


if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("ЗАПУСК ВИРТУАЛЬНОЙ КЛАВИАТУРЫ")
    logger.info("=" * 80)

    root = tk.Tk()
    root.title("Виртуальная клавиатура")
    root.configure(bg='#2b2b2b')
    root.attributes('-topmost', True)
    root.resizable(True, True)
    root.minsize(800, 300)
    root.geometry("1200x400")
    logger.info("Главное окно создано")

    manager = LayoutManager(root)
    manager.current_visualizer.create_keyboard()
    logger.info("Начальная клавиатура создана")

    logger.info("Запуск главного цикла")
    root.mainloop()
    logger.info("Программа завершена")
