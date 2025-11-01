"""
Простая программа для отслеживания нажатий клавиш
Показывает только нажатия (без отпусканий)
Нажмите ESC для выхода
"""

from pynput import keyboard

def on_press(key):
    """Отслеживает нажатие клавиши"""
    try:
        # Обычная клавиша (буква, цифра)
        print(f'Нажата: {key.char}')
    except AttributeError:
        # Специальная клавиша (Enter, Space, Ctrl и т.д.)
        print(f'Нажата: {key}')
        
        # Выход при нажатии ESC
        if key == keyboard.Key.esc:
            print('\nПрограмма завершена!')
            return False

# Запуск программы
print('Отслеживание клавиш запущено. Нажмите ESC для выхода.\n')

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
