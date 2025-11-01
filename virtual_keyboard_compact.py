"""
Компактная виртуальная клавиатура
Простая визуализация нажатий клавиш
"""

import tkinter as tk
from pynput import keyboard
import threading

class CompactKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Компактная клавиатура")
        self.root.configure(bg='#1e1e1e')
        
        self.buttons = {}
        self.press_count = 0
        
        # Упрощенная раскладка
        self.layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['Space']
        ]
        
        self.create_ui()
        threading.Thread(target=self.start_listener, daemon=True).start()
        
    def create_ui(self):
        """Создание интерфейса"""
        frame = tk.Frame(self.root, bg='#1e1e1e', padx=10, pady=10)
        frame.pack()
        
        # Заголовок
        tk.Label(
            frame,
            text="⌨️ Компактная клавиатура",
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, columnspan=10, pady=5)
        
        # Создание клавиш
        for row_idx, row in enumerate(self.layout, start=1):
            for col_idx, key in enumerate(row):
                width = 15 if key == 'Space' else 3
                btn = tk.Label(
                    frame,
                    text=key,
                    width=width,
                    height=2,
                    bg='#3a3a3a',
                    fg='#ffffff',
                    font=('Arial', 10, 'bold'),
                    relief=tk.RAISED,
                    borderwidth=2
                )
                
                col_span = len(row) if key == 'Space' else 1
                btn.grid(row=row_idx, column=col_idx, padx=1, pady=1, columnspan=col_span)
                
                self.buttons[key.lower()] = btn
        
        # Счетчик
        self.counter = tk.Label(
            frame,
            text="Нажатий: 0",
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Arial', 10, 'bold')
        )
        self.counter.grid(row=len(self.layout) + 1, column=0, columnspan=10, pady=5)
    
    def highlight(self, key_name):
        """Подсветка клавиши"""
        key_lower = key_name.lower()
        
        if key_lower in self.buttons:
            btn = self.buttons[key_lower]
            btn.configure(bg='#ffff00', fg='#000000')
            self.root.after(150, lambda: btn.configure(bg='#3a3a3a', fg='#ffffff'))
            
            self.press_count += 1
            self.counter.configure(text=f"Нажатий: {self.press_count}")
    
    def on_press(self, key):
        """Обработчик нажатия"""
        try:
            self.root.after(0, lambda: self.highlight(key.char))
        except AttributeError:
            if str(key) == 'Key.space':
                self.root.after(0, lambda: self.highlight('space'))
    
    def start_listener(self):
        """Запуск слушателя"""
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
    
    def run(self):
        """Запуск"""
        self.root.mainloop()

if __name__ == '__main__':
    print("Запуск компактной клавиатуры...")
    app = CompactKeyboard()
    app.run()
