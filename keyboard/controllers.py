"""
Модуль контроллеров клавиатуры
Содержит базовый класс и конкретные реализации для управления вводом
"""

# Импортируем модуль time для работы с временными метками
import time
# Импортируем ABC (Abstract Base Class) для создания абстрактных классов
# Импортируем abstractmethod - декоратор для абстрактных методов
from abc import ABC, abstractmethod
# Импортируем Dict для аннотации типа словаря
from typing import Dict

# Импортируем базовый класс визуализатора клавиатуры
from .visualizers import BaseKeyboardVisualizer
# Импортируем конфигурации раскладок клавиатуры
from .config import KeyboardLayoutConfig, RussianLayoutConfig
# Импортируем сервис для определения состояния Caps Lock
from .services import CapsLockDetector


class BaseKeyboardController(ABC):
    """Абстрактный базовый класс для управления клавиатурой"""

    def __init__(self, visualizer: BaseKeyboardVisualizer):
        """
        Инициализация базового контроллера клавиатуры

        Args:
            visualizer: Визуализатор клавиатуры для отображения состояния
        """
        # Сохраняем ссылку на визуализатор для обновления GUI
        self.visualizer = visualizer
        # Инициализируем пустую строку для хранения набранного текста
        self.typed_text = ""
        # Устанавливаем максимальную длину отображаемого текста (50 символов)
        self.max_text_length = 50
        # Синхронизируем состояние Caps Lock с системным при запуске
        # Используем CapsLockDetector для проверки реального состояния клавиши
        self.caps_lock_on = CapsLockDetector.is_caps_lock_on()
        # Флаг состояния клавиши Shift (изначально не нажата)
        self.shift_pressed = False
        # Создаём копию маппинга специальных клавиш из конфигурации
        # copy() нужен, чтобы не изменять исходный словарь
        self.key_mapping = KeyboardLayoutConfig.SPECIAL_KEY_MAPPING.copy()
        # Время последнего нажатия backspace для защиты от двойного срабатывания
        self.last_backspace_time = 0

    @abstractmethod
    def process_character(self, char: str) -> str:
        """
        Обработка символа с учетом языка (абстрактный метод)

        Этот метод должен быть реализован в классах-наследниках
        для обработки символов с учётом правил конкретного языка

        Args:
            char: Символ для обработки

        Returns:
            str: Обработанный символ
        """
        pass

    def add_character(self, char: str):
        """
        Добавление символа в набранный текст

        Args:
            char: Символ для добавления
        """
        # Проверяем, что символ не является None
        if char is not None:
            # Обрабатываем символ с учётом языка (вызываем абстрактный метод)
            processed_char = self.process_character(char)
            # Добавляем обработанный символ к набранному тексту
            self.typed_text += processed_char

            # Проверяем, не превысил ли текст максимальную длину
            if len(self.typed_text) > self.max_text_length:
                # Обрезаем текст, оставляя только последние max_text_length символов
                # [-50:] берёт последние 50 символов из строки
                self.typed_text = self.typed_text[-self.max_text_length:]

            # Обновляем отображение текста в визуализаторе
            self.visualizer.update_text_display(self.typed_text)

    def handle_special_key(self, key_name: str):
        """
        Обработка специальных клавиш (Backspace, Space, Enter, Esc, Caps Lock)

        Args:
            key_name: Название специальной клавиши
        """
        # Проверяем, является ли нажатая клавиша клавишей Backspace
        if key_name == 'backspace':
            # Получаем текущее время для защиты от двойного срабатывания
            current_time = time.time()
            # Если прошло менее 50 миллисекунд с последнего backspace, игнорируем
            if current_time - self.last_backspace_time < 0.05:
                return
            # Обновляем время последнего нажатия backspace
            self.last_backspace_time = current_time
            # Проверяем, есть ли набранный текст для удаления
            if self.typed_text:
                # Удаляем последний символ (срез [:-1] берёт все символы кроме последнего)
                self.typed_text = self.typed_text[:-1]
                # Обновляем отображение текста на экране
                self.visualizer.update_text_display(self.typed_text)
        # Проверяем, является ли клавиша пробелом
        elif key_name == 'space':
            # Добавляем символ пробела к набранному тексту
            self.add_character(' ')
        # Проверяем, является ли клавиша Enter
        elif key_name == 'enter':
            # Очищаем весь набранный текст
            self.typed_text = ""
            # Обновляем отображение (показываем пустую строку)
            self.visualizer.update_text_display(self.typed_text)
        # Проверяем, является ли клавиша Esc
        elif key_name == 'esc':
            # Очищаем весь набранный текст
            self.typed_text = ""
            # Обновляем отображение (показываем пустую строку)
            self.visualizer.update_text_display(self.typed_text)
        # Проверяем, является ли клавиша Caps Lock
        elif key_name == 'caps_lock':
            # Синхронизируемся с системным состоянием Caps Lock вместо простого переключения
            # Это важно, т.к. пользователь мог изменить Caps Lock вне приложения
            self.caps_lock_on = CapsLockDetector.is_caps_lock_on()

    def on_press(self, key):
        """
        Обработка события нажатия клавиши (вызывается pynput.keyboard.Listener)

        Args:
            key: Объект клавиши из pynput (может быть Key или KeyCode)
        """
        try:
            # Пытаемся получить атрибут char (символ клавиши)
            # Это работает для обычных символьных клавиш (a, b, 1, 2, и т.д.)
            key_char = key.char
            # Обрабатываем символьную клавишу
            self._handle_character_key(key_char)
        except AttributeError:
            # Если у клавиши нет атрибута char - это специальная клавиша
            # (Shift, Ctrl, Backspace, Enter, и т.д.)
            # Конвертируем объект клавиши в строку и убираем префикс 'Key.'
            # Например: Key.shift -> shift, Key.backspace -> backspace
            key_name = str(key).replace('Key.', '')
            # Обрабатываем специальную клавишу
            self._handle_special_key_press(key_name)

    def on_release(self, key):
        """
        Обработка события отпускания клавиши (вызывается pynput.keyboard.Listener)

        Args:
            key: Объект клавиши из pynput
        """
        try:
            # Конвертируем объект клавиши в строку и убираем префикс 'Key.'
            key_name = str(key).replace('Key.', '')
            # Проверяем, является ли отпущенная клавиша клавишей Shift (левой или правой)
            if key_name in ['shift', 'shift_r']:
                # Устанавливаем флаг Shift в False (клавиша отпущена)
                self.shift_pressed = False
        except AttributeError:
            # Игнорируем любые ошибки при обработке отпускания клавиши
            pass

    @abstractmethod
    def _handle_character_key(self, key_char: str):
        """
        Обработка символьной клавиши (абстрактный метод)

        Этот метод должен быть реализован в классах-наследниках
        для обработки обычных символьных клавиш

        Args:
            key_char: Символ нажатой клавиши
        """
        pass

    def _handle_special_key_press(self, key_name: str):
        """
        Обработка нажатия специальной клавиши

        Args:
            key_name: Название специальной клавиши
        """
        # Проверяем, является ли клавиша клавишей Shift (левой или правой)
        if key_name in ['shift', 'shift_r']:
            # Устанавливаем флаг Shift в True (клавиша нажата)
            self.shift_pressed = True
        # Планируем подсветку клавиши в главном потоке GUI
        # after(0, ...) выполняет функцию в главном потоке как можно скорее
        # lambda нужна для отложенного вызова с параметрами
        self.visualizer.root.after(0, lambda: self.visualizer.highlight_key(key_name, self.key_mapping))
        # Планируем обработку специальной клавиши в главном потоке
        self.visualizer.root.after(0, lambda: self.handle_special_key(key_name))

    def get_typed_text(self) -> str:
        """
        Получение текущего набранного текста

        Returns:
            str: Текст, набранный пользователем
        """
        # Возвращаем сохранённый набранный текст
        return self.typed_text

    def set_typed_text(self, text: str):
        """
        Установка набранного текста (используется при переключении раскладки)

        Args:
            text: Текст для установки
        """
        # Сохраняем переданный текст
        self.typed_text = text
        # Проверяем, существует ли визуализатор и его текстовое поле
        if self.visualizer and self.visualizer.text_display:
            try:
                # Пытаемся обновить отображение текста
                self.visualizer.update_text_display(self.typed_text)
            except:
                # Игнорируем ошибки (могут возникнуть при переключении раскладок)
                pass

    def sync_caps_lock_state(self):
        """
        Синхронизация состояния Caps Lock с системным

        Вызывается при переключении раскладки для синхронизации
        внутреннего состояния с реальным состоянием системной клавиши
        """
        # Обновляем состояние Caps Lock из системы через CapsLockDetector
        self.caps_lock_on = CapsLockDetector.is_caps_lock_on()


class EnglishKeyboardController(BaseKeyboardController):
    """Контроллер английской клавиатуры"""

    def process_character(self, char: str) -> str:
        """
        Обработка английского символа с учётом Caps Lock и Shift

        Args:
            char: Символ для обработки

        Returns:
            str: Обработанный символ (в верхнем или нижнем регистре)
        """
        # Проверяем, является ли символ буквой
        if char.isalpha():
            # Используем XOR логику для определения регистра:
            # - Caps Lock ВКЛ + Shift НЕ нажат = ЗАГЛАВНЫЕ (True != False = True)
            # - Caps Lock ВКЛ + Shift нажат = строчные (True != True = False)
            # - Caps Lock ВЫКЛ + Shift нажат = ЗАГЛАВНЫЕ (False != True = True)
            # - Caps Lock ВЫКЛ + Shift НЕ нажат = строчные (False != False = False)
            if self.caps_lock_on != self.shift_pressed:
                # Возвращаем символ в верхнем регистре
                return char.upper()
            else:
                # Возвращаем символ в нижнем регистре
                return char.lower()
        # Для небуквенных символов (цифры, знаки) возвращаем без изменений
        return char

    def _handle_character_key(self, key_char: str):
        """
        Обработка нажатия символьной клавиши

        Args:
            key_char: Символ нажатой клавиши
        """
        # Планируем подсветку клавиши в главном потоке GUI
        # after(0, ...) выполняет функцию в главном потоке как можно скорее
        self.visualizer.root.after(0, lambda: self.visualizer.highlight_key(key_char, self.key_mapping))
        # Планируем добавление символа к тексту в главном потоке
        self.visualizer.root.after(0, lambda: self.add_character(key_char))


class RussianKeyboardController(BaseKeyboardController):
    """Контроллер русской клавиатуры"""

    def __init__(self, visualizer: BaseKeyboardVisualizer):
        """
        Инициализация контроллера русской клавиатуры

        Args:
            visualizer: Визуализатор клавиатуры для отображения состояния
        """
        # Вызываем конструктор базового класса для инициализации общих полей
        super().__init__(visualizer)
        # Создаём словарь для хранения времени последнего нажатия каждой клавиши
        # Используется для защиты от дублирования символов при быстром нажатии
        self.last_key_time: Dict[str, float] = {}
        # Получаем карту преобразования английских символов в русские из конфигурации
        self.en_to_ru_map = RussianLayoutConfig.EN_TO_RU_MAP

    def process_character(self, char: str) -> str:
        """
        Обработка русского символа (конвертация из английского с учётом регистра)

        Args:
            char: Английский символ для конвертации

        Returns:
            str: Русский символ с правильным регистром
        """
        # Сначала применяем Caps Lock и Shift к английскому символу
        # Проверяем, является ли символ буквой
        if char.isalpha():
            # Используем XOR логику для определения регистра
            # (аналогично английскому контроллеру)
            if self.caps_lock_on != self.shift_pressed:
                # Переводим английский символ в верхний регистр
                char = char.upper()
            else:
                # Переводим английский символ в нижний регистр
                char = char.lower()

        # Конвертируем английский символ (с учётом регистра) в русский
        # Проверяем, есть ли символ в карте преобразования
        if char in self.en_to_ru_map:
            # Возвращаем соответствующий русский символ из карты
            return self.en_to_ru_map[char]
        # Если символа нет в карте (например, цифры или знаки), возвращаем как есть
        return char

    def _handle_character_key(self, key_char: str):
        """
        Обработка нажатия символьной клавиши с защитой от дублирования

        Args:
            key_char: Символ нажатой клавиши
        """
        # Получаем текущее время в секундах с начала эпохи Unix
        current_time = time.time()
        # Проверяем, нажималась ли эта клавиша ранее
        if key_char in self.last_key_time:
            # Вычисляем разницу во времени между текущим и предыдущим нажатием
            time_diff = current_time - self.last_key_time[key_char]
            # Если прошло менее 50 миллисекунд (0.05 секунды)
            if time_diff < 0.05:
                # Игнорируем это нажатие (защита от дублирования)
                return

        # Сохраняем время текущего нажатия для этой клавиши
        self.last_key_time[key_char] = current_time

        # Для подсветки нужно конвертировать английский символ в русский
        # Начинаем с исходного английского символа
        highlight_char = key_char
        # Проверяем, является ли символ буквой
        if key_char.isalpha():
            # Применяем логику Caps Lock и Shift для определения регистра
            if self.caps_lock_on != self.shift_pressed:
                # Переводим в верхний регистр
                highlight_char = key_char.upper()
            else:
                # Переводим в нижний регистр
                highlight_char = key_char.lower()

        # Конвертируем английский символ в русский для подсветки
        if highlight_char in self.en_to_ru_map:
            # Заменяем на соответствующий русский символ
            highlight_char = self.en_to_ru_map[highlight_char]

        # Используем closure (замыкание) для захвата значений переменных
        # Это нужно, т.к. lambda будет выполняться позже, и значения могут измениться
        def do_highlight(hc=highlight_char):
            # Подсвечиваем русский символ на виртуальной клавиатуре
            self.visualizer.highlight_key(hc, self.key_mapping)

        def do_add(kc=key_char):
            # Добавляем символ к набранному тексту (будет сконвертирован в process_character)
            self.add_character(kc)

        # Планируем подсветку клавиши в главном потоке GUI
        self.visualizer.root.after(0, do_highlight)
        # Планируем добавление символа к тексту в главном потоке
        self.visualizer.root.after(0, do_add)