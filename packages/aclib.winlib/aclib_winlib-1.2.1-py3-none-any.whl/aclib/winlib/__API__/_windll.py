import ctypes as _ctypes
from . import _wintype

kernel32 = _ctypes.windll.kernel32
user32 = _ctypes.windll.user32
gdi32 = _ctypes.windll.gdi32
ole32 = _ctypes.windll.ole32
shell32 = _ctypes.windll.shell32
comdlg32 = _ctypes.windll.comdlg32
advapi32 = _ctypes.windll.advapi32

_kernel32 = kernel32
_user32 = user32
_gdi32 = gdi32
_ole32 = ole32
_shell32 = shell32
_comdlg32 = comdlg32
_advapi32 = advapi32

_WM_ARGTYPES = _wintype.HWND, _wintype.UINT, _wintype.WPARAM, _wintype.LPARAM
_user32.DefWindowProcW.argtypes = _WM_ARGTYPES
_user32.PostThreadMessageW.argtypes = _WM_ARGTYPES
_user32.SendMessageW.argtypes = _WM_ARGTYPES
_user32.PostMessageW.argtypes = _WM_ARGTYPES
_user32.PostThreadMessageW.argtypes = _WM_ARGTYPES

_user32.CreateWindowExW.argtypes = (
    _wintype.DWORD, _wintype.LPCWSTR, _wintype.LPCWSTR, _wintype.DWORD,
    _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int,
    _wintype.HWND, _wintype.HMENU, _wintype.HINSTANCE, _wintype.LPVOID
)

_shell32.SHBrowseForFolderW.restype = _wintype.LPVOID
