"""
Главный файл для запуска виртуальной клавиатуры
Точка входа в приложение
"""

import tkinter as tk

from keyboard.config import UIConfig
from keyboard.manager import LayoutManager


class VirtualKeyboardApp:
    """Главное приложение виртуальной клавиатуры"""

    def __init__(self):
        self.root = self._create_window()
        self.manager = LayoutManager(self.root)
        self.manager.current_visualizer.create_keyboard()

    def _create_window(self) -> tk.Tk:
        """Создание главного окна"""
        root = tk.Tk()
        root.title("Виртуальная клавиатура")
        root.configure(bg=UIConfig.BG_COLOR)
        root.attributes('-topmost', True)
        root.resizable(True, True)
        root.minsize(UIConfig.MIN_WINDOW_WIDTH, UIConfig.MIN_WINDOW_HEIGHT)
        root.geometry(f"{UIConfig.DEFAULT_WINDOW_WIDTH}x{UIConfig.DEFAULT_WINDOW_HEIGHT}")
        return root

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == '__main__':
    app = VirtualKeyboardApp()
    app.run()