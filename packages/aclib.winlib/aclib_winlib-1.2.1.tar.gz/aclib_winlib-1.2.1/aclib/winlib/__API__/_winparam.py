from __future__ import annotations as _annotations

from typing import overload as _overload

from ._windll import _ole32, _ctypes, _gdi32, _user32, _shell32, _comdlg32, _advapi32, _kernel32
from . import _wincon, _wintype

def MakeKeyCode(key: int | str) -> int:
    from string import printable
    if isinstance(key, int):
        return int(0 <= key < 256) and key
    if isinstance(key, str) and len(key) == 1 and key in printable:
        return _user32.VkKeyScanA(ord(key)) & 0xff
    if isinstance(key, str):
        vkname = 'VK_' + key.upper() \
            .replace('NUMPAD+', 'ADD') \
            .replace('NUMPAD-', 'SUBTRACT') \
            .replace('NUMPAD*', 'MULTIPLY') \
            .replace('NUMPAD/', 'DIVIDE')
        return getattr(_wincon, vkname, 0)
    raise TypeError(
        'int or str expected')

def MakeKeyMessageParam(key):
    wparam = MakeKeyCode(key)
    scancode = _user32.MapVirtualKeyW(wparam, 0)
    keydown_lparam = (scancode << 16) | 1
    keyup_lparam = (scancode << 16) | 0XC0000001
    return (wparam, keydown_lparam), (wparam, keyup_lparam)

def MakeLong(loword=0, hiword=0) -> int:
    return hiword << 16 | loword

def ParseLong(param) -> tuple[int, int]:
    loword, hiword = param & 0xffff, param >> 16
    return loword, hiword

def ParseSYSTEMTIME(systemtime: _wintype.SYSTEMTIME, UTCdiff = +8) -> float:
    from datetime import datetime
    return datetime(
        systemtime.wYear,
        systemtime.wMonth,
        systemtime.wDay,
        systemtime.wHour,
        systemtime.wMinute,
        systemtime.wSecond,
        systemtime.wMilliseconds * 1000
    ).timestamp() + UTCdiff * 3600

def _transferpoint(method, hwnd, args):
    point, ret = _wintype.POINT(), ()
    for i in range(0, len(args), 2):
        point.x, point.y = args[i], args[i + 1]
        method(hwnd, _ctypes.byref(point))
        ret += point.x, point.y
    return ret

@_overload
def ClientToScreen(hwnd, x: int, y: int): ...
@_overload
def ClientToScreen(hwnd, x1: int, y1: int, x2: int, y2: int): ...
def ClientToScreen(hwnd, *args):
    return _transferpoint(_user32.ClientToScreen, hwnd, args)

@_overload
def ScreenToClient(hwnd, x: int, y: int): ...
@_overload
def ScreenToClient(hwnd, x1: int, y1: int, x2: int, y2: int): ...
def ScreenToClient(hwnd, *args):
    return _transferpoint(_user32.ScreenToClient, hwnd, args)
