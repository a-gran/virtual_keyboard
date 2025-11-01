"""
Программа для отслеживания нажатий клавиш
Нажмите ESC для выхода из программы
"""

from pynput import keyboard
import time

# Переменная для хранения времени начала работы
start_time = time.time()

def on_press(key):
    """
    Функция вызывается при нажатии клавиши
    """
    try:
        # Получаем время с начала работы программы
        elapsed_time = time.time() - start_time
        
        # Если нажата обычная клавиша (буква, цифра и т.д.)
        print(f'[{elapsed_time:.2f}s] Нажата клавиша: {key.char}')
    except AttributeError:
        # Если нажата специальная клавиша (Ctrl, Alt, Shift и т.д.)
        print(f'[{elapsed_time:.2f}s] Нажата специальная клавиша: {key}')

def on_release(key):
    """
    Функция вызывается при отпускании клавиши
    """
    elapsed_time = time.time() - start_time
    
    try:
        print(f'[{elapsed_time:.2f}s] Отпущена клавиша: {key.char}')
    except AttributeError:
        print(f'[{elapsed_time:.2f}s] Отпущена специальная клавиша: {key}')
    
    # Если нажата клавиша ESC - выходим из программы
    if key == keyboard.Key.esc:
        print('\n--- Программа завершена ---')
        return False

def main():
    """
    Основная функция программы
    """
    print('='*50)
    print('Программа отслеживания нажатий клавиш запущена!')
    print('Нажмите ESC для выхода')
    print('='*50)
    print()
    
    # Создаём слушатель клавиатуры
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
        listener.join()

if __name__ == '__main__':
    main()
