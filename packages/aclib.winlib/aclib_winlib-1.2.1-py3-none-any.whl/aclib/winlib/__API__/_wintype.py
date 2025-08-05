# from: https://learn.microsoft.com/en-us/windows/win32/winprog/windows-data-types

import sys as _sys, ctypes as _ctypes
from ctypes import Structure as _Structure

_WIN64 = _sys.maxsize > 2 ** 32

# ==================== ckeyword ====================
#define WINAPI __stdcall
#define CALLBACK __stdcall
#define APIENTRY WINAPI
#define VOID void
#define CONST const
#define POINTER_SIGNED __sptr
#define POINTER_UNSIGNED __uptr
# if _WIN64:
    #define POINTER_32 __ptr32
    #define POINTER_64 __ptr64
# else:
    #define POINTER_32
    #define POINTER_64

# ==================== cint/cstr ====================

BYTE = _ctypes.c_ubyte  # usigned char
CHAR = CCHAR = _ctypes.c_char
UCHAR = _ctypes.c_ubyte # usigned char
WCHAR = _ctypes.c_wchar
# TCHAR = WCHAR if _UNICODE else CHAR
# TBYTE = WCHAR if _UNICODE else CHAR

BOOL = _ctypes.c_int
BOOLEAN = BYTE
FLOAT = _ctypes.c_float

WORD = _ctypes.c_ushort
DWORD = _ctypes.c_ulong
DWORDLONG = _ctypes.c_uint64
DWORD32 = _ctypes.c_uint32
DWORD64 = _ctypes.c_uint64
QWORD = _ctypes.c_uint64

INT = _ctypes.c_int
INT8 = _ctypes.c_int8
INT16 = _ctypes.c_int16
INT32 = _ctypes.c_int32
INT64 = _ctypes.c_int64

UINT = _ctypes.c_uint
UINT8 = _ctypes.c_uint8
UINT16 = _ctypes.c_uint16
UINT32 = _ctypes.c_uint32
UINT64 = _ctypes.c_uint64

LONG = _ctypes.c_long
LONG32 = _ctypes.c_int32
LONG64 = _ctypes.c_int64
# LONGLONG = _ctypes.c_double if _M_IX86 else _ctypes.c_int64

ULONG = _ctypes.c_ulong
ULONG32 = _ctypes.c_uint32
ULONG64 = _ctypes.c_uint64
# ULONGLONG = _ctypes.c_double if _M_IX86 else _ctypes.c_uint64

SHORT = _ctypes.c_short
USHORT = _ctypes.c_ushort

if _WIN64:
    HALF_PTR = _ctypes.c_int
    INT_PTR = _ctypes.c_int64
    LONG_PTR = _ctypes.c_int64
    UHALF_PTR = _ctypes.c_uint
    UINT_PTR = _ctypes.c_uint64
    ULONG_PTR = _ctypes.c_uint64
else:
    HALF_PTR = _ctypes.c_short
    INT_PTR = _ctypes.c_int
    LONG_PTR = _ctypes.c_long
    UHALF_PTR = _ctypes.c_ushort
    UINT_PTR = _ctypes.c_uint
    ULONG_PTR = _ctypes.c_ulong
DWORD_PTR = ULONG_PTR

SIZE_T = ULONG_PTR
SSIZE_T = LONG_PTR
WPARAM = UINT_PTR
LPARAM = LONG_PTR
LRESULT = LONG_PTR

ATOM = WORD
COLORREF = DWORD
LANGID = WORD
LCID = DWORD
LCTYPE = DWORD
LGRPID = DWORD
# UNICODE_STRING
# USN = LONGLONG

# ==================== cpointer ====================
# LPCTSTR | LPTSTR | PCTSTR | PTSTR <-- equals respective column of 2nd line if _UNICODE else of 1st line
LPCSTR    = LPSTR  = PCSTR  = PSTR  = _ctypes.c_char_p    # if _ANSI
LPCWSTR   = LPWSTR = PCWSTR = PWSTR = _ctypes.c_wchar_p   # if _UNICODE

LPCVOID = LPVOID = PVOID = _ctypes.c_void_p
SC_LOCK = LPVOID

# ==================== handle ====================
HANDLE = PVOID
HACCEL = HANDLE
HBITMAP = HANDLE
HBRUSH = HANDLE
HCOLORSPACE = HANDLE
HCONV = HANDLE
HCONVLIST = HANDLE
HCURSOR = HANDLE
HDC = HANDLE
HDDEDATA = HANDLE
HDESK = HANDLE
HDROP = HANDLE
HDWP = HANDLE
HENHMETAFILE = HANDLE
HFILE = HANDLE
HFONT = HANDLE
HGDIOBJ = HANDLE
HGLOBAL = HANDLE
HHOOK = HANDLE
HICON = HANDLE
HINSTANCE = HANDLE
HKEY = HANDLE
HKL = HANDLE
HLOCAL = HANDLE
HMENU = HANDLE
HMETAFILE = HANDLE
HMODULE = HANDLE
HMONITOR = HANDLE
HPALETTE = HANDLE
HPEN = HANDLE
HRESULT = HANDLE
HRGN = HANDLE
HRSRC = HANDLE
HSZ = HANDLE
HWINSTA = HANDLE
HWND = HANDLE
SC_HANDLE = HANDLE
SERVICE_STATUS_HANDLE = HANDLE

# ==================== pointer ====================
PBYTE = LPBYTE = _ctypes.POINTER(BYTE)
PCHAR = _ctypes.POINTER(CHAR)
PUCHAR = _ctypes.POINTER(UCHAR)
PWCHAR = _ctypes.POINTER(WCHAR)
# PTCHAR = PWCHAR if _UNICODE else PCHAR
# PTBYTE = PWCHAR if _UNICODE else PCHAR

PBOOL = LPBOOL = _ctypes.POINTER(BOOL)
PBOOLEAN = _ctypes.POINTER(BOOLEAN)
PFLOAT = _ctypes.POINTER(FLOAT)

PWORD = LPWORD = _ctypes.POINTER(WORD)
PDWORD = LPDWORD = _ctypes.POINTER(DWORD)
PDWORDLONG = _ctypes.POINTER(DWORDLONG)
PDWORD32 = _ctypes.POINTER(DWORD32)
PDWORD64 = _ctypes.POINTER(DWORD64)

PINT = LPINT = _ctypes.POINTER(INT)
PINT8 = _ctypes.POINTER(INT8)
PINT16 = _ctypes.POINTER(INT16)
PINT32 = _ctypes.POINTER(INT32)
PINT64 = _ctypes.POINTER(INT64)

PUINT = _ctypes.POINTER(UINT)
PUINT8 = _ctypes.POINTER(UINT8)
PUINT16 = _ctypes.POINTER(UINT16)
PUINT32 = _ctypes.POINTER(UINT32)
PUINT64 = _ctypes.POINTER(UINT64)

PLONG = LPLONG = _ctypes.POINTER(LONG)
PLONG32 = _ctypes.POINTER(LONG32)
PLONG64 = _ctypes.POINTER(LONG64)
# PLONGLONG = _ctypes.POINTER(LONGLONG)

PULONG = _ctypes.POINTER(ULONG)
PULONG32 = _ctypes.POINTER(ULONG32)
PULONG64 = _ctypes.POINTER(ULONG64)
# PULONGLONG = _ctypes.POINTER(ULONGLONG)

PSHORT = _ctypes.POINTER(SHORT)
PUSHORT = _ctypes.POINTER(USHORT)

PHALF_PTR = _ctypes.POINTER(HALF_PTR)
PINT_PTR = _ctypes.POINTER(INT_PTR)
PLONG_PTR = _ctypes.POINTER(LONG_PTR)
PUHALF_PTR = _ctypes.POINTER(UHALF_PTR)
PUINT_PTR = _ctypes.POINTER(UINT_PTR)
PULONG_PTR = _ctypes.POINTER(ULONG_PTR)
PDWORD_PTR = _ctypes.POINTER(DWORD_PTR)

PSIZE_T = _ctypes.POINTER(SIZE_T)
PSSIZE_T = _ctypes.POINTER(SSIZE_T)

LPCOLORREF = _ctypes.POINTER(COLORREF)
PLCID = _ctypes.POINTER(LCID)
PHANDLE = LPHANDLE = _ctypes.POINTER(HANDLE)
PHKEY = _ctypes.POINTER(HKEY)

# ==================== function ====================
WNDPROC = _ctypes.WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)
WNDENUMPROC = _ctypes.WINFUNCTYPE(BOOL, HWND, LPARAM)
WINEVENTPROC = _ctypes.WINFUNCTYPE(None, HANDLE, DWORD, HWND, LONG, LONG, DWORD, DWORD)

# ==================== structure ====================
class _Structure(_Structure):

    @classmethod
    def sizeof(cls):
        return _ctypes.sizeof(cls)

    @property
    def ref(self):
        return _ctypes.byref(self)

    @property
    def pointer(self):
        return _ctypes.pointer(self)

    def keys(self):
        for k, _ in self._fields_:
            yield k

    def values(self):
        for k, _ in self._fields_:
            yield getattr(self, k)

    def items(self):
        for k, _ in self._fields_:
            yield k, getattr(self, k)

    def __repr__(self):
        data = {k: getattr(self, k) for k, _ in self._fields_}
        return f'<cStructure.{self.__class__.__name__} {data}>'

def _make_fields(kwargs: dict):
    return [*filter(lambda item: item[0][0] != '_', kwargs.items())]


class WNDCLASSEXW(_Structure):
    cbSize          = UINT
    style           = UINT
    lpfnWndProc     = WNDPROC
    cbClsExtra      = _ctypes.c_int
    cbWndExtra      = _ctypes.c_int
    hInstance       = HINSTANCE
    hIcon           = HICON
    hCursor         = HCURSOR
    hbrBackground   = HBRUSH
    lpszMenuName    = LPCWSTR
    lpszClassName   = LPCWSTR
    hIconSm         = HICON
    _fields_ = _make_fields(locals())

class RECT(_Structure):
    left:   int = LONG
    top:    int = LONG
    right:  int = LONG
    bottom: int = LONG
    _fields_ = _make_fields(locals())

    @property
    def start(self):
        return self.left, self.top

    @property
    def end(self):
        return self.right, self.bottom

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def size(self):
        return self.width, self.height

class POINT(_Structure):
    x = LONG
    y = LONG
    _fields_ = _make_fields(locals())

class MSG(_Structure):
    hwnd        = HWND
    message     = UINT
    wParam      = WPARAM
    lParam      = LPARAM
    time        = DWORD
    pt          = POINT
    _fields_ = _make_fields(locals())

class FILETIME(_Structure):
    dwLowDateTime    = DWORD
    dwHighDateTime   = DWORD
    _fields_ = _make_fields(locals())

class SYSTEMTIME(_Structure):
    wYear           = WORD
    wMonth          = WORD
    wDayOfWeek      = WORD
    wDay            = WORD
    wHour           = WORD
    wMinute         = WORD
    wSecond         = WORD
    wMilliseconds   = WORD
    _fields_ = _make_fields(locals())

class PAINTSTRUCT(_Structure):
    hdc         = HDC
    fErase      = BOOL
    rcPaint     = RECT
    fRestore    = BOOL
    fIncUpdate  = BOOL
    rgbReserved = BYTE * 32
    _fields_ = _make_fields(locals())

BFFCALLBACK = _ctypes.WINFUNCTYPE(_ctypes.c_int, HWND, UINT, LPARAM, LPARAM)

class BROWSEINFOW(_Structure):
    hwndOwner       = HWND
    pidlRoot        = LPVOID
    pszDisplayName  = LPWSTR
    lpszTitle       = LPCWSTR
    ulFlags         = UINT
    lpfn            = BFFCALLBACK
    lParam          = LPARAM
    iImage          = _ctypes.c_int
    _fields_ = _make_fields(locals())

class CREATESTRUCTW(_Structure):
    lpCreateParams  = LPVOID
    hInstance       = HINSTANCE
    hMenu           = HMENU
    hwndParent      = HWND
    cy              = _ctypes.c_int
    cx              = _ctypes.c_int
    y               = _ctypes.c_int
    x               = _ctypes.c_int
    style           = LONG
    lpszName        = LPCWSTR
    lpszClass       = LPCWSTR
    dwExStyle       = DWORD
    _fields_ = _make_fields(locals())

class TRACKMOUSEEVENT(_Structure):
    cbSize      = DWORD
    dwFlags     = DWORD
    hwndTrack   = HWND
    dwHoverTime = DWORD
    _fields_ = _make_fields(locals())

class BITMAPINFOHEADER(_Structure):
    biSize          = DWORD
    biWidth         = LONG
    biHeight        = LONG
    biPlanes        = WORD
    biBitCount      = WORD
    biCompression   = DWORD
    biSizeImage     = DWORD
    biXPelsPerMeter = LONG
    biYPelsPerMeter = LONG
    biClrUsed       = DWORD
    biClrImportant  = DWORD
    _fields_ = _make_fields(locals())

class RGBQUAD(_Structure):
    rgbBlue     = BYTE
    rgbGreen    = BYTE
    rgbRed      = BYTE
    rgbReserved = BYTE
    _fields_ = _make_fields(locals())

class BITMAPINFO(_Structure):
    bmiHeader       = BITMAPINFOHEADER
    bmiColors       = RGBQUAD * 256
    _fields_ = _make_fields(locals())

class WINDOWPOS(_Structure):
    hwnd            = HWND
    hwndInsertAfter = HWND
    x               = INT
    y               = INT
    cx              = INT
    cy              = INT
    flags           = UINT
    _fields_ = _make_fields(locals())

class NCCALCSIZE_PARAMS(_Structure):
    rgrc            = RECT * 3
    lppos           = WINDOWPOS
    _fields_ = _make_fields(locals())

class OPENFILENAMEW(_Structure):
    lStructSize     = DWORD
    hwndOwner       = HWND
    hInstance       = HINSTANCE
    lpstrFilter     = LPCWSTR
    lpstrCustomFilter = LPWSTR
    nMaxCustFilter  = DWORD
    nFilterIndex    = DWORD
    lpstrFile       = LPWSTR
    nMaxFile        = DWORD
    lpstrFileTitle  = LPWSTR
    nMaxFileTitle   = DWORD
    lpstrInitialDir = LPCWSTR
    lpstrTitle      = LPCWSTR
    Flags           = DWORD
    nFileOffset     = WORD
    nFileExtension  = WORD
    lpstrDefExt     = LPCWSTR
    lCustData       = LPARAM
    lpfnHook        = LPVOID
    lpTemplateName  = LPCWSTR
    _fields_ = _make_fields(locals())
