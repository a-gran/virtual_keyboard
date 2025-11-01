"""
Улучшенная виртуальная клавиатура с эффектами и статистикой
Клавиши подсвечиваются с плавной анимацией
"""

import tkinter as tk
from pynput import keyboard
import threading
from collections import defaultdict
import time

class EnhancedVirtualKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎹 Виртуальная клавиатура - Расширенная версия")
        self.root.configure(bg='#1a1a1a')
        
        # Словари для кнопок и статистики
        self.buttons = {}
        self.key_stats = defaultdict(int)
        self.last_key_time = {}
        
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
            'esc': 'Esc', 'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4',
            'f5': 'F5', 'f6': 'F6', 'f7': 'F7', 'f8': 'F8',
            'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12',
            'backspace': 'Backspace', 'tab': 'Tab', 'caps_lock': 'Caps',
            'enter': 'Enter', 'shift': 'Shift', 'shift_r': 'Shift',
            'ctrl': 'Ctrl', 'ctrl_r': 'Ctrl', 'alt': 'Alt', 'alt_r': 'Alt',
            'cmd': 'Win', 'cmd_r': 'Win', 'space': 'Space', 'menu': 'Menu',
        }
        
        self.press_count = 0
        self.start_time = time.time()
        
        self.create_keyboard()
        
        # Запуск слушателя клавиатуры
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()
        
        # Обновление статистики
        self.update_stats()
        
    def create_keyboard(self):
        """Создание визуальной клавиатуры"""
        main_frame = tk.Frame(self.root, bg='#1a1a1a', padx=15, pady=15)
        main_frame.pack()
        
        # Заголовок
        title_frame = tk.Frame(main_frame, bg='#1a1a1a')
        title_frame.grid(row=0, column=0, columnspan=15, pady=10)
        
        title = tk.Label(
            title_frame, 
            text="🎹 ВИРТУАЛЬНАЯ КЛАВИАТУРА",
            bg='#1a1a1a',
            fg='#00ffff',
            font=('Arial', 14, 'bold')
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Нажимайте клавиши на физической клавиатуре для визуализации",
            bg='#1a1a1a',
            fg='#888888',
            font=('Arial', 9)
        )
        subtitle.pack()
        
        # Создание рядов клавиш
        for row_idx, row in enumerate(self.keyboard_layout, start=1):
            row_frame = tk.Frame(main_frame, bg='#1a1a1a')
            row_frame.grid(row=row_idx, column=0, columnspan=15, pady=3)
            
            for key in row:
                width = self.get_key_width(key)
                
                # Создание кнопки с градиентным эффектом
                btn = tk.Label(
                    row_frame,
                    text=key,
                    width=width,
                    height=2,
                    relief=tk.RAISED,
                    bg='#2d2d2d',
                    fg='#e0e0e0',
                    font=('Consolas', 10, 'bold'),
                    borderwidth=3,
                    cursor='hand2'
                )
                btn.pack(side=tk.LEFT, padx=2)
                
                # Сохранение кнопки
                key_lower = key.lower()
                if key_lower not in self.buttons:
                    self.buttons[key_lower] = []
                self.buttons[key_lower].append(btn)
        
        # Панель статистики
        stats_frame = tk.Frame(main_frame, bg='#252525', relief=tk.GROOVE, borderwidth=2)
        stats_frame.grid(row=len(self.keyboard_layout) + 1, column=0, columnspan=15, pady=15, sticky='ew')
        
        # Счетчики
        counters_frame = tk.Frame(stats_frame, bg='#252525')
        counters_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.total_label = tk.Label(
            counters_frame,
            text="Всего нажатий: 0",
            bg='#252525',
            fg='#00ff00',
            font=('Arial', 11, 'bold')
        )
        self.total_label.grid(row=0, column=0, padx=20, pady=5)
        
        self.speed_label = tk.Label(
            counters_frame,
            text="Скорость: 0.0 кл/сек",
            bg='#252525',
            fg='#ffaa00',
            font=('Arial', 11, 'bold')
        )
        self.speed_label.grid(row=0, column=1, padx=20, pady=5)
        
        self.last_key_label = tk.Label(
            counters_frame,
            text="Последняя клавиша: -",
            bg='#252525',
            fg='#00aaff',
            font=('Arial', 11, 'bold')
        )
        self.last_key_label.grid(row=0, column=2, padx=20, pady=5)
        
        self.top_key_label = tk.Label(
            counters_frame,
            text="Топ клавиша: -",
            bg='#252525',
            fg='#ff00ff',
            font=('Arial', 11, 'bold')
        )
        self.top_key_label.grid(row=0, column=3, padx=20, pady=5)
        
    def get_key_width(self, key):
        """Определение ширины клавиши"""
        special_widths = {
            'Backspace': 10, 'Tab': 6, 'Caps': 7, 'Enter': 9,
            'Shift': 8, 'Ctrl': 5, 'Win': 5, 'Alt': 5,
            'Space': 25, 'Menu': 5, 'Esc': 5
        }
        return special_widths.get(key, 4)
    
    def highlight_key(self, key_name):
        """Подсветка клавиши с анимацией"""
        key_lower = key_name.lower()
        
        # Поиск кнопок для подсветки
        buttons_to_highlight = []
        
        if key_lower in self.buttons:
            buttons_to_highlight = self.buttons[key_lower]
        else:
            for mapped_key, display_key in self.key_mapping.items():
                if mapped_key in key_lower or key_lower == mapped_key:
                    display_lower = display_key.lower()
                    if display_lower in self.buttons:
                        buttons_to_highlight = self.buttons[display_lower]
                        break
        
        # Анимация подсветки
        for btn in buttons_to_highlight:
            # Яркая подсветка
            btn.configure(
                bg='#00ff88',
                fg='#000000',
                relief=tk.SUNKEN,
                borderwidth=4
            )
            
            # Промежуточный цвет через 100ms
            self.root.after(100, lambda b=btn: b.configure(
                bg='#00aa55',
                relief=tk.RAISED
            ))
            
            # Возврат к нормальному цвету через 250ms
            self.root.after(250, lambda b=btn: b.configure(
                bg='#2d2d2d',
                fg='#e0e0e0',
                borderwidth=3
            ))
        
        # Обновление статистики
        self.press_count += 1
        self.key_stats[key_name] += 1
        self.last_key_time[key_name] = time.time()
        
        # Обновление метки последней клавиши
        display_name = key_name.upper() if len(key_name) == 1 else key_name.title()
        self.last_key_label.configure(text=f"Последняя клавиша: {display_name}")
    
    def on_press(self, key):
        """Обработка нажатия клавиши"""
        try:
            key_char = key.char
            self.root.after(0, lambda: self.highlight_key(key_char))
        except AttributeError:
            key_name = str(key).replace('Key.', '')
            self.root.after(0, lambda: self.highlight_key(key_name))
    
    def start_listener(self):
        """Запуск слушателя клавиатуры"""
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
    
    def update_stats(self):
        """Обновление статистики"""
        # Обновление общего счетчика
        self.total_label.configure(text=f"Всего нажатий: {self.press_count}")
        
        # Расчет скорости
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            speed = self.press_count / elapsed_time
            self.speed_label.configure(text=f"Скорость: {speed:.1f} кл/сек")
        
        # Топ клавиша
        if self.key_stats:
            top_key = max(self.key_stats.items(), key=lambda x: x[1])
            display_name = top_key[0].upper() if len(top_key[0]) == 1 else top_key[0].title()
            self.top_key_label.configure(text=f"Топ клавиша: {display_name} ({top_key[1]}x)")
        
        # Повторное обновление через 500ms
        self.root.after(500, self.update_stats)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

if __name__ == '__main__':
    print("=" * 60)
    print("Запуск улучшенной виртуальной клавиатуры...")
    print("Нажимайте клавиши для визуализации с эффектами!")
    print("=" * 60)
    
    app = EnhancedVirtualKeyboard()
    app.run()
