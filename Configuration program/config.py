"""Pico Configurator - application configuration constants.

기존 control.py에서 설정/표시 관련 상수를 분리한 모듈입니다.
GUI 및 Pico 제어 로직은 변경하지 않습니다.
"""

BUTTON_PINS = [
    "GP20",
    "GP18",
    "GP1",
    "GP9"
]

# 하드웨어에 연결된 고정 버튼 개수
BUTTON_COUNT = 4

DEFAULT_SETTINGS = {
    "buttons": [
        {
            "type": "key",
            "value": ["CONTROL", "C"]
        },
        {
            "type": "key",
            "value": ["CONTROL", "V"]
        },
        {
            "type": "key",
            "value": ["ALT", "TAB"]
        },
        {
            "type": "key",
            "value": ["WINDOWS"]
        }
    ]
}

KEY_MAP = {

    # 알파벳
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "F",
    "g": "G",
    "h": "H",
    "i": "I",
    "j": "J",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "O",
    "p": "P",
    "q": "Q",
    "r": "R",
    "s": "S",
    "t": "T",
    "u": "U",
    "v": "V",
    "w": "W",
    "x": "X",
    "y": "Y",
    "z": "Z",

    # 숫자
    "0": "ZERO",
    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",

    # 기능키
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",

    # 특수키
    "space": "SPACE",
    "return": "ENTER",
    "enter": "ENTER",
    "escape": "ESCAPE",
    "esc": "ESCAPE",
    "tab": "TAB",
    "backspace": "BACKSPACE",
    "delete": "DELETE",
    "insert": "INSERT",

    "home": "HOME",
    "end": "END",

    "prior": "PAGE_UP",
    "next": "PAGE_DOWN",

    # 방향키
    "left": "LEFT_ARROW",
    "right": "RIGHT_ARROW",
    "up": "UP_ARROW",
    "down": "DOWN_ARROW",

    # 조합키
    "control_l": "CONTROL",
    "control_r": "CONTROL",

    "shift_l": "SHIFT",
    "shift_r": "SHIFT",

    "alt_l": "ALT",
    "alt_r": "ALT",

    "win_l": "WINDOWS",
    "win_r": "WINDOWS",

    # 기타
    "caps_lock": "CAPS_LOCK",
    "num_lock": "NUM_LOCK",
    "print": "PRINT_SCREEN",
    "scroll_lock": "SCROLL_LOCK",
    "pause": "PAUSE",
    "menu": "MENU"
}

DISPLAY_NAMES = {

    "CONTROL": "Ctrl",
    "SHIFT": "Shift",
    "ALT": "Alt",
    "WINDOWS": "Windows",

    "ENTER": "Enter",
    "ESCAPE": "Esc",
    "TAB": "Tab",
    "SPACE": "Space",

    "BACKSPACE": "Backspace",
    "DELETE": "Delete",
    "INSERT": "Insert",

    "HOME": "Home",
    "END": "End",

    "PAGE_UP": "Page Up",
    "PAGE_DOWN": "Page Down",

    "LEFT_ARROW": "←",
    "RIGHT_ARROW": "→",
    "UP_ARROW": "↑",
    "DOWN_ARROW": "↓",

    "CAPS_LOCK": "Caps Lock",
    "NUM_LOCK": "Num Lock",
    "PRINT_SCREEN": "Print Screen",
    "SCROLL_LOCK": "Scroll Lock",
    "PAUSE": "Pause",
    "MENU": "Menu"
}
