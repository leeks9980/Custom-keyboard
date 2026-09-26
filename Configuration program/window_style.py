import ctypes
import sys
import tkinter as tk


# Windows DWM 속성
_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_DWMWA_CAPTION_COLOR = 35
_DWMWA_TEXT_COLOR = 36


def _colorref(hex_color):
    """#RRGGBB -> Windows COLORREF(0x00BBGGRR)"""
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return 0
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return r | (g << 8) | (b << 16)


def apply_title_bar_style(window, caption_color="#15171c", text_color="#f2f4f7"):
    """Windows 기본 제목 표시줄을 앱 색상과 맞춘다.

    최소화/최대화/닫기 버튼은 Windows 기본 기능을 그대로 유지한다.
    Windows가 아닌 환경에서는 아무 작업도 하지 않는다.
    """
    if sys.platform != "win32":
        return

    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            hwnd = window.winfo_id()

        dwmapi = ctypes.windll.dwmapi

        dark_mode = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            _DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_mode),
            ctypes.sizeof(dark_mode),
        )

        caption = ctypes.c_int(_colorref(caption_color))
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            _DWMWA_CAPTION_COLOR,
            ctypes.byref(caption),
            ctypes.sizeof(caption),
        )

        text = ctypes.c_int(_colorref(text_color))
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            _DWMWA_TEXT_COLOR,
            ctypes.byref(text),
            ctypes.sizeof(text),
        )
    except Exception:
        # OS 버전/환경에 따라 DWM 속성이 지원되지 않아도 프로그램은 정상 실행한다.
        pass
