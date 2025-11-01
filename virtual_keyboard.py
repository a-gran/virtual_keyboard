"""
Виртуальная клавиатура с визуализацией нажатий клавиш
Клавиши подсвечиваются при нажатии
"""

import tkinter as tk
from pynput import keyboard
import threading

class VirtualKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Виртуальная клавиатура")
        self.root.configure(bg='#2b2b2b')
        
        # Словарь для хранения кнопок
        self.buttons = {}
        
        # Раскладка клавиатуры
        self.keyboard_layout = [
            ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Win', 'Menu', 'Ctrl']
        ]
        
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
        
        # Запуск слушателя клавиатуры в отдельном потоке
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()
        
    def create_keyboard(self):
        """Создание визуальной клавиатуры"""
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        main_frame.pack()
        
        # Заголовок
        title = tk.Label(
            main_frame, 
            text="🎹 Виртуальная клавиатура - Нажимайте клавиши на физической клавиатуре",
            bg='#2b2b2b',
            fg='#ffffff',
            font=('Arial', 12, 'bold'),
            pady=10
        )
        title.grid(row=0, column=0, columnspan=15)
        
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
                btn.pack(side=tk.LEFT, padx=2)
                
                # Сохранение кнопки в словаре
                key_lower = key.lower()
                if key_lower not in self.buttons:
                    self.buttons[key_lower] = []
                self.buttons[key_lower].append(btn)
        
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
    
    def start_listener(self):
        """Запуск слушателя клавиатуры"""
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

if __name__ == '__main__':
    print("Запуск виртуальной клавиатуры...")
    print("Нажимайте клавиши на физической клавиатуре - они будут подсвечиваться!")
    
    app = VirtualKeyboard()
    app.run()
