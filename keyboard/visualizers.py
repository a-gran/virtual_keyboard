"""
Модуль визуализаторов клавиатуры
Содержит базовый класс и конкретные реализации для разных языков
"""

# Импортируем модуль tkinter для создания графического интерфейса
import tkinter as tk
# Импортируем ABC и abstractmethod для создания абстрактных классов
from abc import ABC, abstractmethod
# Импортируем типы для аннотации: Dict, List, Tuple, Optional
from typing import Dict, List, Tuple, Optional

# Импортируем классы конфигурации UI и раскладок клавиатуры
from .config import UIConfig, EnglishLayoutConfig, RussianLayoutConfig


class BaseKeyboardVisualizer(ABC):
    """Абстрактный базовый класс для визуализации клавиатуры"""

    def __init__(self, root: tk.Tk):
        """
        Инициализация базового визуализатора клавиатуры

        Args:
            root: Главное окно приложения Tkinter
        """
        # Сохраняем ссылку на главное окно
        self.root = root
        # Словарь: символ клавиши -> список кнопок Label с этим символом
        # Используется для быстрого поиска кнопок по символу
        self.buttons: Dict[str, List[tk.Label]] = {}
        # Список всех виджетов-кнопок клавиатуры
        self.button_widgets: List[tk.Label] = []
        # Словарь: кнопка -> её базовый цвет (для восстановления после подсветки)
        self.button_colors: Dict[tk.Label, str] = {}
        # Словарь: позиция (строка, колонка) -> кнопка в этой позиции
        self.button_positions: Dict[Tuple[int, int], tk.Label] = {}
        # Коэффициент масштабирования для размеров шрифтов (по умолчанию 1.0)
        self.scale_factor = 1.0
        # Список последних нажатых кнопок (для отслеживания и сброса подсветки)
        self.last_pressed_buttons: List[tk.Label] = []
        # Главный фрейм клавиатуры (может быть None до создания)
        self.main_frame: Optional[tk.Frame] = None
        # Текстовое поле для отображения набранного текста (может быть None)
        self.text_display: Optional[tk.Label] = None

    @abstractmethod
    def get_layout(self) -> List[List[str]]:
        """
        Возвращает раскладку клавиатуры (абстрактный метод)

        Должен быть реализован в классах-наследниках

        Returns:
            List[List[str]]: Двумерный список строк с символами клавиш
        """
        pass

    @abstractmethod
    def get_home_row_keys(self) -> List[str]:
        """
        Возвращает клавиши домашней строки для выделения (абстрактный метод)

        Должен быть реализован в классах-наследниках

        Returns:
            List[str]: Список символов клавиш домашнего ряда (F, J для EN; А, О для RU)
        """
        pass

    @abstractmethod
    def get_title(self) -> str:
        """
        Возвращает заголовок окна (абстрактный метод)

        Должен быть реализован в классах-наследниках

        Returns:
            str: Текст заголовка
        """
        pass

    @abstractmethod
    def get_title_color(self) -> str:
        """
        Возвращает цвет заголовка (абстрактный метод)

        Должен быть реализован в классах-наследниках

        Returns:
            str: Цвет заголовка в формате HEX (#4dabf7 для EN, #ff6b6b для RU)
        """
        pass

    def get_position_weights(self) -> Dict[Tuple[int, int], int]:
        """
        Возвращает веса позиций клавиш для определения относительной ширины

        Returns:
            Dict[Tuple[int, int], int]: Словарь позиция -> вес
        """
        # Импортируем конфигурацию раскладки
        from .config import KeyboardLayoutConfig
        # Возвращаем веса позиций из конфигурации
        return KeyboardLayoutConfig.POSITION_WEIGHTS

    def create_keyboard(self, typed_text: str = ""):
        """
        Создание визуальной клавиатуры

        Главный метод для создания всех элементов GUI клавиатуры

        Args:
            typed_text: Текст для отображения (по умолчанию пустая строка)
        """
        # Если главный фрейм уже существует, удаляем его
        # Это нужно при переключении раскладок
        if self.main_frame is not None:
            self.main_frame.destroy()

        # Сбрасываем внутреннее состояние (очищаем словари и списки)
        self._reset_internal_state()
        # Создаём главный фрейм (контейнер для всех элементов)
        self._create_main_frame()
        # Создаём заголовок с названием и текущим языком
        self._create_title()
        # Создаём текстовый дисплей для отображения набранного текста
        self._create_text_display(typed_text)
        # Создаём раскладку клавиатуры (кнопки)
        self._create_keyboard_layout()

    def _reset_internal_state(self):
        """
        Сброс внутреннего состояния визуализатора

        Очищает все словари и списки, связанные с кнопками
        Используется при переключении раскладок
        """
        # Очищаем словарь маппинга символов на кнопки
        self.buttons = {}
        # Очищаем список всех виджетов-кнопок
        self.button_widgets = []
        # Очищаем словарь базовых цветов кнопок
        self.button_colors = {}
        # Очищаем словарь позиций кнопок
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

            button_size = max(9, int(14 * self.scale_factor))
            btn = tk.Label(
                row_frame,
                text=key,
                relief=tk.RAISED,
                bg=bg_color,
                fg=UIConfig.FG_COLOR,
                font=(UIConfig.FONT_FAMILY, button_size, 'bold'),
                borderwidth=2,
                width=1,
                pady=2
            )
            btn.grid(row=0, column=col_idx, sticky='nsew', padx=UIConfig.SPACING, pady=UIConfig.SPACING)

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


class EnglishKeyboardVisualizer(BaseKeyboardVisualizer):
    """Визуализатор английской (EN) клавиатуры"""

    def get_layout(self) -> List[List[str]]:
        """
        Возвращает английскую раскладку QWERTY

        Returns:
            List[List[str]]: Раскладка из EnglishLayoutConfig
        """
        # Возвращаем конфигурацию английской раскладки QWERTY
        return EnglishLayoutConfig.LAYOUT

    def get_home_row_keys(self) -> List[str]:
        """
        Возвращает клавиши домашнего ряда для английской раскладки

        Returns:
            List[str]: Список ['F', 'J'] - клавиши с выступами
        """
        # Возвращаем клавиши F и J (стандартные для английской раскладки)
        return EnglishLayoutConfig.HOME_ROW_KEYS

    def get_title(self) -> str:
        """
        Возвращает заголовок для английской раскладки

        Returns:
            str: Текст заголовка с эмодзи клавиатуры и указанием языка EN
        """
        # Возвращаем заголовок с иконкой клавиатуры и указанием английского языка
        return "🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: EN"

    def get_title_color(self) -> str:
        """
        Возвращает цвет заголовка для английской раскладки

        Returns:
            str: Голубой цвет (#4dabf7) для английской раскладки
        """
        # Возвращаем голубой цвет для заголовка английской раскладки
        return UIConfig.TITLE_COLOR_EN


class RussianKeyboardVisualizer(BaseKeyboardVisualizer):
    """Визуализатор русской (RU) клавиатуры"""

    def get_layout(self) -> List[List[str]]:
        """
        Возвращает русскую раскладку ЙЦУКЕН

        Returns:
            List[List[str]]: Раскладка из RussianLayoutConfig
        """
        # Возвращаем конфигурацию русской раскладки ЙЦУКЕН
        return RussianLayoutConfig.LAYOUT

    def get_home_row_keys(self) -> List[str]:
        """
        Возвращает клавиши домашнего ряда для русской раскладки

        Returns:
            List[str]: Список ['А', 'О'] - клавиши с выступами
        """
        # Возвращаем клавиши А и О (стандартные для русской раскладки)
        return RussianLayoutConfig.HOME_ROW_KEYS

    def get_title(self) -> str:
        """
        Возвращает заголовок для русской раскладки

        Returns:
            str: Текст заголовка с эмодзи клавиатуры и указанием языка RU
        """
        # Возвращаем заголовок с иконкой клавиатуры и указанием русского языка
        return "🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: RU"

    def get_title_color(self) -> str:
        """
        Возвращает цвет заголовка для русской раскладки

        Returns:
            str: Красный цвет (#ff6b6b) для русской раскладки
        """
        # Возвращаем красный цвет для заголовка русской раскладки
        return UIConfig.TITLE_COLOR_RU