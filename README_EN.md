# Virtual Keyboard

[🇷🇺 Russian version](README.md)

## Description

A real-time keystroke visualization application with support for English and Russian keyboard layouts.
Implemented using OOP principles and modular architecture.

## Project Structure

```text
virtual_keyboard/
├── keyboard/                   # Main application package
│   ├── __init__.py            # Package initialization and public class exports
│   ├── config.py              # Configuration and constants
│   ├── visualizers.py         # Keyboard visualizers
│   ├── controllers.py         # Input handling controllers
│   ├── factory.py             # Component creation factory
│   ├── services.py            # Services (language detection and Caps Lock)
│   └── manager.py             # Layout manager
├── main.py                    # Application entry point
├── README.md                  # Documentation (RU)
├── README_EN.md               # Documentation (EN)
└── ARCHITECTURE.md            # Technical architecture documentation
```

## How to Run

```bash
python main.py
```

## How to Stop the Program

Simply close the virtual keyboard window or press **ESC** on your keyboard.

## Architecture

### OOP Principles

The project is implemented using the following principles:

1. **Inheritance**
   - `BaseKeyboardVisualizer` → `EnglishKeyboardVisualizer`, `RussianKeyboardVisualizer`
   - `BaseKeyboardController` → `EnglishKeyboardController`, `RussianKeyboardController`

2. **Encapsulation**
   - Configuration is extracted into separate classes (`UIConfig`, `LayoutConfig`)
   - Each module has a clear responsibility

3. **Polymorphism**
   - Abstract methods in base classes
   - Different behavior for different languages

4. **Factory Pattern**
   - `KeyboardFactory` for creating components by language

5. **Single Responsibility Principle (SRP)**
   - Each class is responsible for one specific task

### Modules

#### config.py

Configuration and constants:

- `Language` - Enum of supported languages
- `UIConfig` - Interface settings (colors, fonts, sizes)
- `KeyboardLayoutConfig` - Base layout configuration
- `EnglishLayoutConfig` - English layout and home row keys (F, J)
- `RussianLayoutConfig` - Russian layout, home row keys (А, О), and character mapping

#### visualizers.py

Keyboard visualization:

- `BaseKeyboardVisualizer` - Abstract base class
- `EnglishKeyboardVisualizer` - English layout visualizer
- `RussianKeyboardVisualizer` - Russian layout visualizer

#### controllers.py

Input handling:

- `BaseKeyboardController` - Abstract base class with Caps Lock support
- `EnglishKeyboardController` - English layout controller
- `RussianKeyboardController` - Controller with EN→RU character conversion

#### factory.py

Component creation:

- `KeyboardFactory` - Factory for creating visualizers and controllers

#### services.py

Helper services:

- `LanguageDetector` - Detect current keyboard language (Windows API)
- `CapsLockDetector` - Detect Caps Lock state via Windows API

#### manager.py

Layout management:

- `LayoutManager` - Automatic layout switching with state synchronization

## Features

- ✅ Real-time keystroke visualization
- ✅ Support for English and Russian layouts
- ✅ Automatic switching when system layout changes
- ✅ Home row key highlighting (F, J for EN; А, О for RU)
- ✅ Typed text display (up to 50 characters)
- ✅ Full Caps Lock support with automatic system state synchronization
- ✅ Shift support with correct handling in combination with Caps Lock
- ✅ Protection against duplicate key presses
- ✅ Text preservation when switching layouts
- ✅ Caps Lock state preservation when switching layouts
- ✅ No nested loops (optimized code)

## Using the Virtual Keyboard

### Scaling

- **Manual resize**: Drag the corners or edges of the window to resize
- **Fullscreen mode**: Click the ⛶ button in the top right corner to maximize
- **Auto-scaling**: Fonts automatically increase/decrease when window is resized

### Layout Switching

- Simply switch the layout in your system (Alt+Shift or other combination)
- The virtual keyboard automatically synchronizes with the system layout
- Title color changes: blue for EN, red for RU

### Working with Caps Lock

- Caps Lock synchronizes with system state when the program starts
- When Caps Lock is pressed, the program automatically detects the new state
- When switching layouts, Caps Lock state is preserved
- Logic: `Caps Lock XOR Shift` to determine case

## Requirements

- Python 3.7+
- tkinter (usually included in standard Python installation)
- pynput

Install dependencies:

```bash
pip install pynput
```

## Note

⚠️ The use of keystroke tracking programs may be regulated by law.
Use this program only on your own computer and for educational purposes.

## Extension Possibilities

You can modify the program to:

- Save keystrokes to a file
- Count keystroke statistics
- Filter specific keys
- Create hotkeys
- Add support for other languages

## Technical Documentation

For detailed information about the architecture, design patterns, and implementation details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## License

This project is for educational purposes.
