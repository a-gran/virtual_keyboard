"""
Модуль сервисов
Содержит вспомогательные сервисы для работы приложения
"""

import ctypes
from .config import Language


class LanguageDetector:
    """Сервис для определения языка клавиатуры"""

    @staticmethod
    def get_current_language() -> Language:
        """Определение текущего языка клавиатуры в Windows"""
        try:
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            curr_window = user32.GetForegroundWindow()
            thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
            klid = user32.GetKeyboardLayout(thread_id)
            lid = klid & 0xFFFF

            if lid == 0x0419:
                return Language.RUSSIAN
            else:
                return Language.ENGLISH
        except Exception:
            return Language.ENGLISH


class CapsLockDetector:
    """Сервис для определения состояния Caps Lock"""

    @staticmethod
    def is_caps_lock_on() -> bool:
        """Определение состояния Caps Lock в Windows"""
        try:
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            # VK_CAPITAL = 0x14 (код виртуальной клавиши Caps Lock)
            # GetKeyState возвращает состояние клавиши
            # Если младший бит установлен (& 1), то Caps Lock включен
            state = user32.GetKeyState(0x14)
            return bool(state & 1)
        except Exception:
            return False