"""
Виртуальная клавиатура с визуализацией нажатий клавиш
Клавиши подсвечиваются при нажатии
"""

import tkinter as tk
from pynput import keyboard
import threading
import ctypes
import time

class VirtualKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Виртуальная клавиатура")
        self.root.configure(bg='#2b2b2b')

        # Разрешить изменение размера окна
        self.root.resizable(True, True)

        # Словарь для хранения кнопок
        self.buttons = {}
        self.button_widgets = []  # Список всех виджетов кнопок для масштабирования
        self.button_colors = {}  # Словарь для хранения базовых цветов кнопок
        self.button_positions = {}  # Словарь для хранения позиций кнопок (row, col) -> button
        self.column_weights = {}  # Словарь для хранения весов колонок (row_idx, col_idx) -> weight

        # Текущий язык раскладки
        self.current_language = 'EN'

        # Коэффициент масштабирования
        self.scale_factor = 1.0

        # Последняя нажатая кнопка (для тусклой подсветки)
        self.last_pressed_buttons = []

        # Главный фрейм для клавиатуры (будем пересоздавать при смене раскладки)
        self.main_frame = None

        # Английская раскладка клавиатуры (основной символ | символ с Shift)
        self.keyboard_layout_en = [
            ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['` | ~', '1 | !', '2 | @', '3 | #', '4 | $', '5 | %', '6 | ^', '7 | &', '8 | *', '9 | (', '0 | )', '- | _', '= | +', 'Backspace'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[ | {', '] | }', '\\ | |'],
            ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '; | :', '\' | "', 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ', | <', '. | >', '/ | ?', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Win', 'Menu', 'Ctrl']
        ]

        # Русская раскладка клавиатуры (основной символ | символ с Shift)
        self.keyboard_layout_ru = [
            ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['ё | Ё', '1 | !', '2 | "', '3 | №', '4 | ;', '5 | %', '6 | :', '7 | ?', '8 | *', '9 | (', '0 | )', '- | _', '= | +', 'Backspace'],
            ['Tab', 'Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ', '\\ | /'],
            ['Caps', 'Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э', 'Enter'],
            ['Shift', 'Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', '. | ,', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Win', 'Menu', 'Ctrl']
        ]

        # Текущая раскладка
        self.keyboard_layout = self.keyboard_layout_en

        # Фиксированные веса для каждой позиции (row, col) -> weight
        # Это обеспечит одинаковый размер кнопок в обеих раскладках
        self.position_weights = {
            # Ряд 0: F-клавиши
            (0, 0): 5, (0, 1): 4, (0, 2): 4, (0, 3): 4, (0, 4): 4, (0, 5): 4,
            (0, 6): 4, (0, 7): 4, (0, 8): 4, (0, 9): 4, (0, 10): 4, (0, 11): 4, (0, 12): 4,
            # Ряд 1: Цифры
            (1, 0): 4, (1, 1): 4, (1, 2): 4, (1, 3): 4, (1, 4): 4, (1, 5): 4,
            (1, 6): 4, (1, 7): 4, (1, 8): 4, (1, 9): 4, (1, 10): 4, (1, 11): 4, (1, 12): 4, (1, 13): 10,
            # Ряд 2: QWERTY
            (2, 0): 6, (2, 1): 4, (2, 2): 4, (2, 3): 4, (2, 4): 4, (2, 5): 4,
            (2, 6): 4, (2, 7): 4, (2, 8): 4, (2, 9): 4, (2, 10): 4, (2, 11): 4, (2, 12): 4, (2, 13): 4,
            # Ряд 3: ASDF
            (3, 0): 7, (3, 1): 4, (3, 2): 4, (3, 3): 4, (3, 4): 4, (3, 5): 4,
            (3, 6): 4, (3, 7): 4, (3, 8): 4, (3, 9): 4, (3, 10): 4, (3, 11): 4, (3, 12): 9,
            # Ряд 4: ZXCV
            (4, 0): 8, (4, 1): 4, (4, 2): 4, (4, 3): 4, (4, 4): 4, (4, 5): 4,
            (4, 6): 4, (4, 7): 4, (4, 8): 4, (4, 9): 4, (4, 10): 4, (4, 11): 8,
            # Ряд 5: Ctrl, Alt, Space
            (5, 0): 5, (5, 1): 5, (5, 2): 5, (5, 3): 25, (5, 4): 5, (5, 5): 5, (5, 6): 5, (5, 7): 5,
        }

        # Маппинг специальных клавиш
        self.key_mapping = {
            'esc': 'Esc',
            'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4',
            'f5': 'F5', 'f6': 'F6', 'f7': 'F7', 'f8': 'F8',
            'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12',
            'backspace': 'Backspace',
            'tab': 'Tab',
            'caps_lock': 'Caps',
            'enter': 'Enter',
            'shift': 'Shift',
            'shift_r': 'Shift',
            'ctrl': 'Ctrl',
            'ctrl_r': 'Ctrl',
            'alt': 'Alt',
            'alt_r': 'Alt',
            'cmd': 'Win',
            'cmd_r': 'Win',
            'space': 'Space',
            'menu': 'Menu',
        }
        
        self.create_keyboard()

        # Привязка события изменения размера окна
        self.root.bind('<Configure>', self.on_window_resize)

        # Запуск слушателя клавиатуры в отдельном потоке
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()

        # Запуск мониторинга раскладки в отдельном потоке
        self.layout_monitor_thread = threading.Thread(target=self.monitor_layout, daemon=True)
        self.layout_monitor_thread.start()
        
    def create_keyboard(self):
        """Создание визуальной клавиатуры"""
        # Если главный фрейм уже существует - удаляем его
        if self.main_frame is not None:
            self.main_frame.destroy()

        # Очищаем словари
        self.buttons = {}
        self.button_widgets = []
        self.button_colors = {}
        self.button_positions = {}

        # Создаем новый главный фрейм
        self.main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Настройка главного фрейма для растягивания
        self.main_frame.columnconfigure(0, weight=1)

        # Заголовок
        lang_text = self.current_language
        lang_color = '#ff6b6b' if self.current_language == 'RU' else '#4dabf7'
        title_size = max(8, int(12 * self.scale_factor))
        self.title_label = tk.Label(
            self.main_frame,
            text=f"🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: {lang_text}",
            bg='#2b2b2b',
            fg=lang_color,
            font=('Arial', title_size, 'bold'),
            pady=10
        )
        self.title_label.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        # Контейнер для клавиатуры
        keyboard_container = tk.Frame(self.main_frame, bg='#2b2b2b')
        keyboard_container.grid(row=1, column=0, sticky='nsew')
        self.main_frame.rowconfigure(1, weight=1)

        # Создание рядов клавиш
        for row_idx, row in enumerate(self.keyboard_layout):
            # Настройка растягивания для каждого ряда по вертикали
            keyboard_container.rowconfigure(row_idx, weight=1)

            row_frame = tk.Frame(keyboard_container, bg='#2b2b2b')
            row_frame.grid(row=row_idx, column=0, sticky='nsew', pady=5)

            # Настройка растягивания внутри row_frame
            row_frame.rowconfigure(0, weight=1)

            for col_idx, key in enumerate(row):
                # Настройка растягивания колонки с использованием фиксированного веса
                weight = self.position_weights.get((row_idx, col_idx), 4)
                row_frame.columnconfigure(col_idx, weight=weight)

                # Определяем базовый ключ для цвета
                base_key = key.split('|')[0].strip() if '|' in key else key

                # Определяем цвет кнопки (F и J - клавиши для слепой печати)
                if base_key.upper() in ['F', 'J', 'Ф', 'О']:  # F, J и их русские аналоги
                    bg_color = '#5a5a5a'  # Более светлый серый для F и J
                else:
                    bg_color = '#404040'  # Обычный цвет

                # Создание кнопки с фиксированной минимальной шириной
                button_size = max(6, int(10 * self.scale_factor))
                btn = tk.Label(
                    row_frame,
                    text=key,
                    relief=tk.RAISED,
                    bg=bg_color,
                    fg='#ffffff',
                    font=('Arial', button_size, 'bold'),
                    borderwidth=2,
                    width=1  # Минимальная ширина в символах
                )
                btn.grid(row=0, column=col_idx, sticky='nsew', padx=5, pady=0)

                # Сохранение кнопки в словаре для всех символов на клавише
                # Если есть "|", добавляем кнопку для обоих символов
                if '|' in key:
                    symbols = [s.strip() for s in key.split('|')]
                    for symbol in symbols:
                        symbol_lower = symbol.lower()
                        if symbol_lower not in self.buttons:
                            self.buttons[symbol_lower] = []
                        self.buttons[symbol_lower].append(btn)
                        # Также добавляем верхний регистр
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
                    # Также добавляем верхний регистр
                    key_upper = key.upper()
                    if key_upper != key_lower:
                        if key_upper not in self.buttons:
                            self.buttons[key_upper] = []
                        self.buttons[key_upper].append(btn)

                # Сохранение базового цвета кнопки
                self.button_colors[btn] = bg_color

                # Добавление в список для масштабирования
                self.button_widgets.append(btn)

                # Сохранение позиции кнопки для обновления при смене раскладки
                self.button_positions[(row_idx, col_idx)] = btn

        # Настройка растягивания для контейнера клавиатуры
        keyboard_container.columnconfigure(0, weight=1)
        
    def get_key_width(self, key):
        """Определение ширины клавиши"""
        special_widths = {
            'Backspace': 10,
            'Tab': 6,
            'Caps': 7,
            'Enter': 9,
            'Shift': 8,
            'Ctrl': 5,
            'Win': 5,
            'Alt': 5,
            'Space': 25,
            'Menu': 5,
            'Esc': 5
        }
        return special_widths.get(key, 4)

    def get_key_weight(self, key):
        """Определение веса клавиши для grid layout (пропорциональное распределение пространства)"""
        special_weights = {
            'Backspace': 10,
            'Tab': 6,
            'Caps': 7,
            'Enter': 9,
            'Shift': 8,
            'Ctrl': 5,
            'Win': 5,
            'Alt': 5,
            'Space': 25,
            'Menu': 5,
            'Esc': 5
        }
        return special_weights.get(key, 4)
    
    def highlight_key(self, key_name):
        """Подсветка клавиши при нажатии"""
        key_lower = key_name.lower()
        key_upper = key_name.upper()

        # Поиск соответствующей кнопки
        buttons_to_highlight = []

        # Прямое совпадение (проверяем оба регистра)
        if key_lower in self.buttons:
            buttons_to_highlight = self.buttons[key_lower]
        elif key_upper in self.buttons:
            buttons_to_highlight = self.buttons[key_upper]
        elif key_name in self.buttons:
            buttons_to_highlight = self.buttons[key_name]

        # Проверка маппинга
        if not buttons_to_highlight:
            for mapped_key, display_key in self.key_mapping.items():
                if mapped_key in key_lower or key_lower == mapped_key:
                    display_lower = display_key.lower()
                    if display_lower in self.buttons:
                        buttons_to_highlight = self.buttons[display_lower]
                        break

        # Если нажали на ту же клавишу повторно - сбрасываем её
        if buttons_to_highlight and buttons_to_highlight == self.last_pressed_buttons:
            for btn in self.last_pressed_buttons:
                base_color = self.button_colors.get(btn, '#404040')
                btn.configure(bg=base_color, fg='#ffffff')
            self.last_pressed_buttons = []
            return

        # Сброс предыдущей клавиши до базового цвета
        for btn in self.last_pressed_buttons:
            base_color = self.button_colors.get(btn, '#404040')
            btn.configure(bg=base_color, fg='#ffffff')

        # Яркая подсветка при нажатии
        for btn in buttons_to_highlight:
            btn.configure(bg='#00ff00', fg='#000000')

        # Через 200ms переключаем на тусклую подсветку
        def set_dim_color():
            for btn in buttons_to_highlight:
                # Проверяем, что эта кнопка всё ещё является последней нажатой
                if btn in self.last_pressed_buttons:
                    btn.configure(bg='#408040', fg='#ffffff')

        self.root.after(200, set_dim_color)

        # Запоминаем текущую кнопку
        self.last_pressed_buttons = buttons_to_highlight
    
    def on_press(self, key):
        """Обработка нажатия клавиши"""
        try:
            # Обычная клавиша
            key_char = key.char
            self.root.after(0, lambda: self.highlight_key(key_char))
        except AttributeError:
            # Специальная клавиша
            key_name = str(key).replace('Key.', '')
            self.root.after(0, lambda: self.highlight_key(key_name))
    
    def get_keyboard_language(self):
        """Определение текущего языка клавиатуры в Windows"""
        try:
            # Получаем handle активного окна
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            curr_window = user32.GetForegroundWindow()
            thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
            # Получаем текущую раскладку
            klid = user32.GetKeyboardLayout(thread_id)
            # Младшее слово содержит идентификатор языка
            lid = klid & 0xFFFF

            # 0x0409 - English (US), 0x0419 - Russian
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
                    self.current_language = new_language
                    self.root.after(0, self.update_keyboard_layout)
                time.sleep(0.1)  # Проверка каждые 100мс
            except Exception:
                time.sleep(0.1)

    def update_keyboard_layout(self):
        """Обновление отображения клавиатуры при смене раскладки"""
        # Сбрасываем подсветку предыдущей клавиши
        for btn in self.last_pressed_buttons:
            base_color = self.button_colors.get(btn, '#404040')
            btn.configure(bg=base_color, fg='#ffffff')
        self.last_pressed_buttons = []

        # Выбираем нужную раскладку
        if self.current_language == 'RU':
            self.keyboard_layout = self.keyboard_layout_ru
        else:
            self.keyboard_layout = self.keyboard_layout_en

        # Пересоздаем клавиатуру заново с правильными весами колонок
        self.create_keyboard()

    def get_corresponding_key(self, row_idx, col_idx):
        """Получение соответствующей клавиши из другой раскладки"""
        try:
            if self.current_language == 'RU':
                # Ищем в английской раскладке
                return self.keyboard_layout_en[row_idx][col_idx]
            else:
                # Ищем в русской раскладке
                return self.keyboard_layout_ru[row_idx][col_idx]
        except (IndexError, KeyError):
            return None

    def on_window_resize(self, event):
        """Обработка изменения размера окна"""
        # Проверяем, что событие относится к главному окну
        if event.widget != self.root:
            return

        # Вычисляем новый коэффициент масштабирования на основе ширины окна
        base_width = 1200  # Базовая ширина окна
        current_width = event.width
        new_scale = max(0.5, min(3.0, current_width / base_width))

        # Обновляем размер шрифта только если изменение значительное
        if abs(new_scale - self.scale_factor) > 0.1:
            self.scale_factor = new_scale
            self.update_font_sizes()

    def update_font_sizes(self):
        """Обновление размеров шрифтов при масштабировании"""
        # Пересоздаем клавиатуру с новыми размерами шрифтов
        self.create_keyboard()

    def start_listener(self):
        """Запуск слушателя клавиатуры"""
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def run(self):
        """Запуск приложения"""
        # Установка минимального размера окна
        self.root.minsize(800, 300)
        # Установка начального размера окна
        self.root.geometry("1200x400")
        self.root.mainloop()

if __name__ == '__main__':
    print("Запуск виртуальной клавиатуры...")
    print("Нажимайте клавиши на физической клавиатуре - они будут подсвечиваться!")
    print("Раскладка автоматически переключается синхронно с системной (RU/EN)")

    app = VirtualKeyboard()
    app.run()
