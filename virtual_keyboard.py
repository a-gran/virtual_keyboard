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

        # Состояние полноэкранного режима
        self.is_fullscreen = False
        self.previous_geometry = None

        # Словарь для хранения кнопок
        self.buttons = {}
        self.button_widgets = []  # Список всех виджетов кнопок для масштабирования

        # Текущий язык раскладки
        self.current_language = 'EN'

        # Коэффициент масштабирования
        self.scale_factor = 1.0

        # Английская раскладка клавиатуры
        self.keyboard_layout_en = [
            ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Win', 'Menu', 'Ctrl']
        ]

        # Русская раскладка клавиатуры
        self.keyboard_layout_ru = [
            ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['ё', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ', '\\'],
            ['Caps', 'Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э', 'Enter'],
            ['Shift', 'Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', '.', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Win', 'Menu', 'Ctrl']
        ]

        # Текущая раскладка
        self.keyboard_layout = self.keyboard_layout_en
        
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
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель с заголовком и кнопкой полноэкранного режима
        header_frame = tk.Frame(main_frame, bg='#2b2b2b')
        header_frame.grid(row=0, column=0, columnspan=15, sticky='ew')

        # Заголовок
        self.title_label = tk.Label(
            header_frame,
            text="🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: EN",
            bg='#2b2b2b',
            fg='#ffffff',
            font=('Arial', 12, 'bold'),
            pady=10
        )
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопка полноэкранного режима
        self.fullscreen_btn = tk.Button(
            header_frame,
            text="⛶",
            command=self.toggle_fullscreen,
            bg='#404040',
            fg='#ffffff',
            font=('Arial', 16, 'bold'),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        self.fullscreen_btn.pack(side=tk.RIGHT, padx=5)
        
        # Создание рядов клавиш
        for row_idx, row in enumerate(self.keyboard_layout, start=1):
            row_frame = tk.Frame(main_frame, bg='#2b2b2b')
            row_frame.grid(row=row_idx, column=0, columnspan=15, pady=2)
            
            for key in row:
                # Определение ширины клавиши
                width = self.get_key_width(key)
                
                # Создание кнопки
                btn = tk.Label(
                    row_frame,
                    text=key,
                    width=width,
                    height=2,
                    relief=tk.RAISED,
                    bg='#404040',
                    fg='#ffffff',
                    font=('Arial', 10, 'bold'),
                    borderwidth=2
                )
                btn.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)

                # Сохранение кнопки в словаре
                key_lower = key.lower()
                if key_lower not in self.buttons:
                    self.buttons[key_lower] = []
                self.buttons[key_lower].append(btn)

                # Добавление в список для масштабирования
                self.button_widgets.append(btn)
        
        # Счетчик нажатий
        self.counter_label = tk.Label(
            main_frame,
            text="Нажатий: 0",
            bg='#2b2b2b',
            fg='#00ff00',
            font=('Arial', 11, 'bold'),
            pady=10
        )
        self.counter_label.grid(row=len(self.keyboard_layout) + 1, column=0, columnspan=15)
        
        self.press_count = 0
        
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
    
    def highlight_key(self, key_name):
        """Подсветка клавиши при нажатии"""
        key_lower = key_name.lower()
        
        # Поиск соответствующей кнопки
        buttons_to_highlight = []
        
        # Прямое совпадение
        if key_lower in self.buttons:
            buttons_to_highlight = self.buttons[key_lower]
        
        # Проверка маппинга
        for mapped_key, display_key in self.key_mapping.items():
            if mapped_key in key_lower or key_lower == mapped_key:
                display_lower = display_key.lower()
                if display_lower in self.buttons:
                    buttons_to_highlight = self.buttons[display_lower]
                    break
        
        # Подсветка найденных кнопок
        for btn in buttons_to_highlight:
            btn.configure(bg='#00ff00', fg='#000000')
            # Сброс цвета через 200ms
            self.root.after(200, lambda b=btn: b.configure(bg='#404040', fg='#ffffff'))
        
        # Обновление счетчика
        self.press_count += 1
        self.counter_label.configure(text=f"Нажатий: {self.press_count}")
    
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
        # Выбираем нужную раскладку
        if self.current_language == 'RU':
            self.keyboard_layout = self.keyboard_layout_ru
            lang_text = "RU"
            lang_color = '#ff6b6b'
        else:
            self.keyboard_layout = self.keyboard_layout_en
            lang_text = "EN"
            lang_color = '#4dabf7'

        # Обновляем заголовок
        self.title_label.configure(
            text=f"🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре | Язык: {lang_text}",
            fg=lang_color
        )

        # Обновляем текст на кнопках
        for row_idx, row in enumerate(self.keyboard_layout):
            for col_idx, key in enumerate(row):
                # Пропускаем служебные клавиши (они одинаковы в обеих раскладках)
                if key in ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                           'Backspace', 'Tab', 'Caps', 'Enter', 'Shift', 'Ctrl', 'Win', 'Alt', 'Space', 'Menu']:
                    continue

                # Находим соответствующие кнопки и обновляем их текст
                key_lower = key.lower()
                if key_lower in self.buttons:
                    for btn in self.buttons[key_lower]:
                        btn.configure(text=key)

                # Также создаем новую запись в словаре для поиска по новому ключу
                if key_lower not in self.buttons:
                    # Находим старый ключ из другой раскладки
                    old_key = self.get_corresponding_key(row_idx, col_idx)
                    if old_key and old_key.lower() in self.buttons:
                        self.buttons[key_lower] = self.buttons[old_key.lower()]

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

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if not self.is_fullscreen:
            # Сохраняем текущую геометрию
            self.previous_geometry = self.root.geometry()
            # Получаем размеры экрана
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # Устанавливаем окно на весь экран
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.fullscreen_btn.configure(text="⛶", bg='#00ff00')
            self.is_fullscreen = True
        else:
            # Восстанавливаем предыдущий размер
            if self.previous_geometry:
                self.root.geometry(self.previous_geometry)
            self.fullscreen_btn.configure(text="⛶", bg='#404040')
            self.is_fullscreen = False

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
        # Базовые размеры шрифтов
        base_title_size = 12
        base_button_size = 10
        base_counter_size = 11

        # Новые размеры с учетом масштаба
        title_size = max(8, int(base_title_size * self.scale_factor))
        button_size = max(6, int(base_button_size * self.scale_factor))
        counter_size = max(8, int(base_counter_size * self.scale_factor))

        # Обновляем шрифт заголовка
        self.title_label.configure(font=('Arial', title_size, 'bold'))

        # Обновляем шрифты кнопок клавиатуры
        for btn in self.button_widgets:
            btn.configure(font=('Arial', button_size, 'bold'))

        # Обновляем шрифт счетчика
        self.counter_label.configure(font=('Arial', counter_size, 'bold'))

        # Обновляем шрифт кнопки полноэкранного режима
        fullscreen_btn_size = max(12, int(16 * self.scale_factor))
        self.fullscreen_btn.configure(font=('Arial', fullscreen_btn_size, 'bold'))

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
