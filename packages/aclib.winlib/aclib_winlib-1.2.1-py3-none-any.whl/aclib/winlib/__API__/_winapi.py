from __future__ import annotations as _annotations
from typing import TYPE_CHECKING as _TYPE_CHECKING

if _TYPE_CHECKING:
    from typing import Iterator as _Iterator, Iterable as _Iterable
    _Pos = _Size = tuple[int, int]

from . import _wincon, _wintype
from ._windll import _ctypes, _user32, _kernel32, _gdi32, _ole32, _shell32, _advapi32, _comdlg32
from ._winparam import *

import _thread
import os as _os
import sys as _sys
import time as _time

def GetScreenSize():
    return (_user32.GetSystemMetrics(_wincon.SM_CXVIRTUALSCREEN),
            _user32.GetSystemMetrics(_wincon.SM_CYVIRTUALSCREEN))

def CoInitialize():
    return _ole32.CoInitialize(0)

def IsUserAdmin():
    return bool(_shell32.IsUserAnAdmin())

def RunAsAdmin(filename=_sys.argv[0], showCmd=True):
    _shell32.ShellExecuteW(None, "runas", _sys.executable, filename, None, int(showCmd))

# region ==> 硬件
# ==============================================================================================================
def GetAsyncKeyState(vkcode) -> bool:
    _user32.GetAsyncKeyState(vkcode)
    return bool(_user32.GetAsyncKeyState(vkcode))   # keydown or not

def GetCursorPos() -> tuple[int, int]:
    point = _wintype.POINT()
    _user32.GetCursorPos(point.ref)
    return point.x, point.y

def SetCursorPos(pos: tuple[int, int]) -> bool:
    return bool(_user32.SetCursorPos(*pos))   # success or not
# endregion

# region ==> 检索特殊窗口
# ==============================================================================================================
def GetPointWindow(pos) -> int:
    return _user32.WindowFromPoint(_wintype.POINT(*pos))

def GetForegroundWindow() -> int:
    return _user32.GetForegroundWindow()

def GetDesktopWindow() -> int:
    return _user32.GetDesktopWindow()

def GetDesktopView() -> int:
    for htop in FilterWindows(IterChildWindows(GetDesktopWindow()), '', '\f Progman', visible=True):
        wndtree = [htop]
        for clsname in ['\f SHELLDLL_DefView', '\f SysListView32', '\f SysHeader32', '']:
            children = [*IterChildWindows(wndtree[-1])]
            if clsname and len(children) != 1:
                break
            child = FilterWindow(children, '', clsname)
            if child:
                wndtree.append(child)
        if len(wndtree) == 4:
            return wndtree[2]

def GetTaskbarWindow() -> int:
    return FilterWindow(IterChildWindows(GetDesktopWindow()), '', '\f Shell_TrayWnd', True)
# endregion

# region ==> 检索关联窗口
# ==============================================================================================================
def GetParentWindow(hwnd) -> int:
    return _user32.GetAncestor(hwnd, _wincon.GA_PARENT)

def GetRootWindow(hwnd) -> int:
    return _user32.GetAncestor(hwnd, _wincon.GA_ROOT)

def GetRootOwnerWindow(hwnd) -> int:
    return _user32.GetAncestor(hwnd, _wincon.GA_ROOTOWNER)

def GetPrevWindow(hwnd) -> int:
    return _user32.GetWindow(hwnd, _wincon.GW_HWNDPREV)

def GetNextWindow(hwnd) -> int:
    return _user32.GetWindow(hwnd, _wincon.GW_HWNDNEXT)

def IterChildWindows(hParent) -> _Iterator[int]:
    if hParent == 0:
        yield GetDesktopWindow()
    if hParent:
        hChild = _user32.GetWindow(hParent, _wincon.GW_CHILD)
        while hChild:
            yield hChild
            hChild = GetNextWindow(hChild)

def IterBrotherWindows(hwnd) -> _Iterator[int]:
    if hwnd:
        return (hbrother for hbrother in IterChildWindows(GetParentWindow(hwnd)) if hbrother != hwnd)
    if hwnd == 0:
        return [].__iter__()

def IterDescendantWindows(hAncestor) -> _Iterator[int]:
    for hChild in IterChildWindows(hAncestor):
        yield hChild
        for hdescendant in IterDescendantWindows(hChild):
            yield hdescendant

def FilterWindow(hwnds: _Iterable[int], title='', classname='', visible: bool=None) -> int:
    for hwnd in FilterWindows(hwnds, title, classname, visible):
        return hwnd
    return 0

def FilterWindows(hwnds: _Iterable[int], title='', classname='', visible=None) -> _Iterator[int]:
    r"""if title/classname startswith '\\f ', filter will execute fullmatch(ignore first '\\f ')"""
    def match(pattern: str, string: str):
        if pattern.startswith('\f '):
            return string == pattern[2:]
        return string.find(pattern) > -1
    for hwnd in hwnds:
        if title and not match(title, GetWindowTitle(hwnd)):
            continue
        if classname and not match(classname, GetWindowClassName(hwnd)):
            continue
        if visible is None or visible == IsWindowVisible(hwnd):
            yield hwnd
# endregion

# region ==> 窗口属性
# ==============================================================================================================
def GetWindowLong(hwnd: int, target: int) -> int:
    return _user32.GetWindowLongW(hwnd, target)

def GetWindowClassName(hwnd: int) -> str:
    clsname = _ctypes.create_unicode_buffer(256)
    _user32.GetClassNameW(hwnd, clsname, 256)
    return clsname.value

def GetWindowTitle(hwnd) -> str:
    textlen = _user32.GetWindowTextLengthW(hwnd)
    title = _ctypes.create_unicode_buffer(textlen + 1)
    _user32.GetWindowTextW(hwnd, title, textlen + 1)
    return title.value

def SetWindowTitle(hwnd, title) -> bool:
    return bool(_user32.SetWindowTextW(hwnd, title))    # success or not

def GetWindowThreadProcessId(hwnd) -> tuple[int, int]:
    processid = _ctypes.c_int(0)
    threadid = _user32.GetWindowThreadProcessId(hwnd, _ctypes.byref(processid))
    return threadid, processid.value
# endregion

# region ==> 窗口显示状态
# ==============================================================================================================
def IsWindowExistent(hwnd) -> bool:
    return bool(_user32.IsWindow(hwnd))

def IsWindowEnabled(hwnd) -> bool:
    return bool(_user32.IsWindowEnabled(hwnd))

def IsWindowVisible(hwnd) -> bool:
    return bool(_user32.IsWindowVisible(hwnd))

def IsWindowMaximized(hwnd) -> bool:
    return bool(_user32.IsZoomed(hwnd))

def IsWindowMinimized(hwnd) -> bool:
    return bool(_user32.IsIconic(hwnd))

def IsWindowNormalized(hwnd) -> bool:
    return not IsWindowMaximized(hwnd) and not IsWindowMinimized(hwnd)

def IsWindowTopMost(hwnd) -> bool:
    return bool(GetWindowLong(hwnd, _wincon.GWL_EXSTYLE) & _wincon.WS_EX_TOPMOST)

def CloseWindow(hwnd):
    SendMessage(hwnd, _wincon.WM_CLOSE, 0, 0)

def DestroyWindow(hwnd):
    SendMessage(hwnd, _wincon.WM_DESTROY, 0, 0)
    SendMessage(hwnd, _wincon.WM_CLOSE, 0, 0)

def EnableWindow(hwnd):
    _user32.EnableWindow(hwnd, 1)

def DisableWindow(hwnd):
    _user32.EnableWindow(hwnd, 0)

def ShowWindow(hwnd):
    _user32.ShowWindow(hwnd, _wincon.SW_SHOWNA)

def HideWindow(hwnd):
    _user32.ShowWindow(hwnd, _wincon.SW_HIDE)

def MaximizeWindow(hwnd):
    if IsWindowMinimized(hwnd):
        NormalizeWindow(hwnd)
    _user32.ShowWindow(hwnd, _wincon.SW_MAXIMIZE)

def MinimizeWindow(hwnd):
    _user32.ShowWindow(hwnd, _wincon.SW_MINIMIZE)

def NormalizeWindow(hwnd):
    _user32.ShowWindow(hwnd, _wincon.SW_SHOWNOACTIVATE)

def SetWindowTopMost(hwnd, topmost: bool):
    toparg = topmost and _wincon.HWND_TOPMOST or _wincon.HWND_NOTOPMOST
    _user32.SetWindowPos(hwnd, toparg, 0, 0, 0, 0, _wincon.SWP_NOMOVE | _wincon.SWP_NOSIZE)
# endregion

# region ==> 窗口类型
# ==============================================================================================================
def IsLayeredWindow(hwnd) -> bool:
    return GetWindowLong(hwnd, _wincon.GWL_EXSTYLE) & _wincon.WS_EX_LAYERED

def LayerWindow(hwnd):
    wndexstyle = GetWindowLong(hwnd, _wincon.GWL_EXSTYLE)
    _user32.SetWindowLongW(hwnd, _wincon.GWL_EXSTYLE, wndexstyle | _wincon.WS_EX_LAYERED)

def UnlayerWindow(hwnd):
    wndexstyle = GetWindowLong(hwnd, _wincon.GWL_EXSTYLE)
    _user32.SetWindowLongW(hwnd, _wincon.GWL_EXSTYLE, wndexstyle - wndexstyle & _wincon.WS_EX_LAYERED)
# endregion

# region ==> 窗口视图信息
# ==============================================================================================================
def GetWindowRect(hwnd) -> _wintype.RECT:
    rect = _wintype.RECT()
    _user32.GetWindowRect(hwnd, rect.ref)
    return rect

def GetWindowRectR(hwnd) -> _wintype.RECT:
    return _wintype.RECT(*ScreenToClient(GetParentWindow(hwnd), *GetWindowRect(hwnd).values()))

def GetClientRect(hwnd) -> _wintype.RECT:
    rect = _wintype.RECT()
    _user32.GetClientRect(hwnd, rect.ref)
    return _wintype.RECT(*ClientToScreen(hwnd, *rect.values()))

def GetClientRectR(hwnd) -> _wintype.RECT:
    return _wintype.RECT(*ScreenToClient(GetParentWindow(hwnd), *GetClientRect(hwnd).values()))

def SetWindowPosSize(hwnd, newpos: _Pos = None, newsize: _Size = None):
    """相对于屏幕左上角"""
    currentrect = GetWindowRect(hwnd)
    newpos, newsize = newpos or currentrect.start, newsize or currentrect.size
    newposR = ScreenToClient(GetParentWindow(hwnd), *newpos)
    repaint = newsize != currentrect.size
    _user32.MoveWindow(hwnd, *newposR, *newsize, repaint)

def SetWindowPosSizeR(hwnd, newposR: _Pos = None, newsize: _Size = None):
    """相对于父窗客户区左上角"""
    newpos = ClientToScreen(GetParentWindow(hwnd), *newposR) if newposR else newposR
    SetWindowPosSize(hwnd, newpos, newsize)

def SetClientPosSize(hwnd, newclientpos: _Pos = None, newclientsize: _Size = None):
    """相对于屏幕左上角"""
    curntclintrect = GetClientRect(hwnd)
    curntwndowrectR = GetWindowRectR(hwnd)
    newclientpos, newclientsize = newclientpos or curntclintrect.start, newclientsize or curntclintrect.size
    dpos = [newclientpos[i] - curntclintrect.start[i] for i in range(2)]
    dsize = [newclientsize[i] - curntclintrect.size[i] for i in range(2)]
    newwindowposR = [curntwndowrectR.start[i] + dpos[i] for i in range(2)]
    newwindowsize = [curntwndowrectR.size[i] + dsize[i] for i in range(2)]
    repaint = newwindowsize != curntwndowrectR.size
    _user32.MoveWindow(hwnd, *newwindowposR, *newwindowsize, repaint)

def SetClientPosSizeR(hwnd, newclientposR: _Pos = None, newclientsize: _Size = None):
    """相对于父窗客户区左上角"""
    newclientpos = ClientToScreen(GetParentWindow(hwnd), *newclientposR) if newclientposR else newclientposR
    SetClientPosSize(hwnd, newclientpos, newclientsize)

def GetWindowTransparency(hwnd) -> float:
    if IsLayeredWindow(hwnd):
        cByte = _ctypes.c_byte(256)
        _user32.GetLayeredWindowAttributes(hwnd, _wincon.NULL, _ctypes.byref(cByte), _wincon.LWA_ALPHA)
        alpha = cByte.value if cByte.value >= 0 else 256 + cByte.value
        return alpha / 255
    return 1.0

def SetWindowTransparency(hwnd, transparency: float):
    if transparency < 0 or transparency > 1:
        raise ValueError(
            'transparency shoud be between 0 and 1.')
    _user32.SetLayeredWindowAttributes(hwnd, _wincon.NULL, round(255 * transparency), _wincon.LWA_ALPHA)

def SetWindowIcon(hwnd, iconpath):
    hicon = _user32.LoadImageW(0, iconpath, _wincon.IMAGE_ICON, 0, 0, _wincon.LR_LOADFROMFILE)
    SendMessage(hwnd, _wincon.WM_SETICON, _wincon.ICON_SMALL, hicon)
# endregion

# region ==> 窗口内容
# ==============================================================================================================
def CaptureWindow(hwnd, area: tuple[int, int, int, int] = None) -> tuple[_Size, bytearray]:
    captureArea = area or [0, 0, *GetClientRect(hwnd).size]
    captureStart = captureArea[:2]
    captureSize = (captureArea[2] - captureArea[0], captureArea[3] - captureArea[1])
    dc = _user32.GetDC(hwnd)
    cdc = _gdi32.CreateCompatibleDC(dc)
    bitmap = _gdi32.CreateCompatibleBitmap(dc, *captureSize)
    _gdi32.SelectObject(cdc, bitmap)
    _gdi32.BitBlt(cdc, 0, 0, *captureSize, dc, *captureStart, _wincon.SRCCOPY)
    total_bytes = captureSize[0] * captureSize[1] * 4
    buffer = bytearray(total_bytes)
    byte_array = _ctypes.c_ubyte * total_bytes
    _gdi32.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
    _gdi32.DeleteObject(bitmap)
    _gdi32.DeleteObject(cdc)
    _user32.ReleaseDC(hwnd, dc)
    return captureSize, buffer

def GetPixel(hwnd, pos: _Pos) -> int:
    dc = _user32.GetDC(hwnd)
    decimalBgr = _gdi32.GetPixel(dc, *pos)
    _user32.ReleaseDC(hwnd, dc)
    return decimalBgr
# endregion

# region ==> Windows消息
# ==============================================================================================================
def SendMessage(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
    result = _user32.SendMessageW(hwnd, msg, wparam, lparam)
    return result

def PostMessage(hwnd: int, msg: int, wparam: int, lparam: int) -> bool:
    success = bool(_user32.PostMessageW(hwnd, msg, wparam, lparam))
    return success

def PostThreadMessage(threadid: int, msg: int, wparam: int, lparam: int) -> bool:
    success = bool(_user32.PostThreadMessageW(threadid, msg, wparam, lparam))
    return success

def PostQuitMessage(exitcode=0):
    _user32.PostQuitMessage(exitcode)

def GetMessageAndTransfer(outMsg: _wintype.MSG, hwnd=0, msgFilterMin=0, msgFilterMax=0) -> bool:
    noquitmsg = _user32.GetMessageW(outMsg.ref, hwnd, msgFilterMin, msgFilterMax)
    _user32.TranslateMessage(outMsg.ref)
    _user32.DispatchMessageW(outMsg.ref)
    return noquitmsg

def PeekMessageAndTransfer(outMsg: _wintype.MSG, hwnd=0, msgFilterMin=0, msgFilterMax=0) -> bool:
    hasmsg = _user32.PeekMessageW(outMsg.ref, hwnd, msgFilterMin, msgFilterMax, 1)
    if hasmsg:
        _user32.TranslateMessage(outMsg.ref)
        _user32.DispatchMessageW(outMsg.ref)
    return hasmsg

def TrackMouseEvent(hwnd: int, trackhover=True, trackleave=True, hovertime=1):
    data = _wintype.TRACKMOUSEEVENT()
    data.cbSize = _ctypes.sizeof(_wintype.TRACKMOUSEEVENT)
    data.hwndTrack = hwnd
    data.dwFlags = _wincon.TME_HOVER * trackhover | _wincon.TME_LEAVE * trackleave
    data.dwHoverTime = hovertime
    _user32.TrackMouseEvent(data.ref)
# endregion

# region ==> 句柄
# ==============================================================================================================
def CloseHandle(handle):
    _kernel32.CloseHandle(handle)
# endregion

# region ==> 进程
# ==============================================================================================================
def GetCurrentProcessId() -> int:
    return _kernel32.GetCurrentProcessId()
# endregion

# region ==> 线程
# ==============================================================================================================
def GetCurrentThreadId() -> int:
    return _kernel32.GetCurrentThreadId()

def OpenThreadHandle(threadid) -> int:
    handle = _kernel32.OpenThread(_wincon.THREAD_ALL_ACCESS, 1, threadid)
    return handle

def OpenCurrentThreadHandle() -> int:
    return OpenThreadHandle(GetCurrentThreadId())

def GetCurrentThreadPseudoHandle() -> int:
    return _kernel32.GetCurrentThread()

def RusumeThread(hthread):
    while _kernel32.ResumeThread(hthread) > 1: pass

def SuspendThread(hthread):
    if _kernel32.SuspendThread(hthread) > 0: _kernel32.ResumeThread(hthread)

def TerminateThread(hthread, exit_code=-1):
    _kernel32.TerminateThread(hthread, exit_code)

def ExitCurrentThread(exit_code=0):
    _kernel32.ExitThread(exit_code)

def IsThreadExited(hthread) -> bool:
    filetime = _wintype.FILETIME()
    exittime = _wintype.FILETIME()
    _kernel32.GetThreadTimes(hthread, filetime.ref, exittime.ref, filetime.ref, exittime.ref)
    return bool(exittime.dwLowDateTime)

def GetThreadExitCode(hthread) -> int:
    exitcode = _ctypes.c_int(0)
    _kernel32.GetExitCodeThread(hthread, _ctypes.byref(exitcode))
    return exitcode.value

def GetThreadTimes(hthread, UTCdiff = +8) -> list[int]:
    returntimes = []
    filetimes = [_wintype.FILETIME(), _wintype.FILETIME(), _wintype.FILETIME(), _wintype.FILETIME()]
    _kernel32.GetThreadTimes(hthread, *(ftime.ref for ftime in filetimes))
    for filetime in filetimes:
        returntimes.append(0)
        systemtime = _wintype.SYSTEMTIME()
        _kernel32.FileTimeToSystemTime(filetime.ref, systemtime.ref)
        if systemtime.wYear > 1601:
            returntimes[-1] = ParseSYSTEMTIME(systemtime, UTCdiff)
    return returntimes      # return: [creationTime, exitTime, timeAmountInKernelMode, timeAmountInUserMode]
# endregion

# region ==> 消息循环线程
# ==============================================================================================================
_MSGLOOP_TASK_QUEUES: dict[int, list[tuple[function, tuple, dict, list]]] = {}
def __msgloop_thread_(lpReady: list):
    msg = _wintype.MSG()
    loopid = GetCurrentThreadId()
    _MSGLOOP_TASK_QUEUES[loopid] = []
    lpReady.append(True)
    while GetMessageAndTransfer(msg):
        while _MSGLOOP_TASK_QUEUES.get(loopid, []):
            task = _MSGLOOP_TASK_QUEUES[loopid].pop(0)
            func, args, kwargs, lpResponse = task
            lpResponse.append(func(*args, **kwargs))

def CreateMsgloopThread():
    ready = []
    loopthreadid = _thread.start_new_thread(__msgloop_thread_, (ready,))
    while not ready:
        _time.sleep(.001)
    return loopthreadid

def RequestMsgloopTask(func, loopthreadid, *args, **kwargs):
    if loopthreadid in _MSGLOOP_TASK_QUEUES:
        lpResponse = []
        task = (func, args, kwargs, lpResponse)
        _MSGLOOP_TASK_QUEUES[loopthreadid].append(task)
        start, overtime = _time.time(), 1
        while PostThreadMessage(loopthreadid, _wincon.WM_APP+1, GetCurrentThreadId(), GetCurrentThreadId()) == 0:
            if _time.time() - start > overtime:
                raise _ctypes.WinError(
                    _kernel32.GetLastError(), "request overtime, see https://learn.microsoft.com/zh-cn/windows/win32/debug/system-error-codes")
        while not lpResponse:
            _time.sleep(.001)
        return lpResponse[0]
    return None

def DestroyMsgloopThread(loopthreadid):
    if loopthreadid in _MSGLOOP_TASK_QUEUES:
        _MSGLOOP_TASK_QUEUES.pop(loopthreadid, None)
        PostThreadMessage(loopthreadid, _wincon.WM_QUIT, 0, 0)
# endregion

# region ==> 窗口类管理
# ==============================================================================================================
_WndClassRuntimeData = {}

def RegisterWindowClass(classname: str, msgCBK = None, args = None, kwargs = None) -> _wintype.WNDCLASSEXW:
    """回调函数返回 None 时自动调用 DefWindowProcW 作为 wndproc 的返回值"""
    def finalMsgCBK(hwnd, message, wParam, lParam):
        ret = msgCBK and msgCBK(hwnd, message, wParam, lParam, *args or (), **kwargs or {})
        return _user32.DefWindowProcW(hwnd, message, wParam, lParam) if ret is None else ret
    wndclass = _wintype.WNDCLASSEXW()
    wndclass.cbSize         = _ctypes.sizeof(_wintype.WNDCLASSEXW)
    wndclass.style          = _wincon.CS_HREDRAW | _wincon.CS_VREDRAW | _wincon.CS_DBLCLKS
    wndclass.lpfnWndProc    = _wintype.WNDPROC(finalMsgCBK)
    wndclass.hIcon          = _user32.LoadIconW(0, _wincon.IDI_APPLICATION)
    wndclass.hbrBackground  = _gdi32.GetStockObject(_wincon.WHITE_BRUSH)
    wndclass.lpszClassName  = classname
    if not _user32.RegisterClassExW(wndclass.ref):
        raise _ctypes.WinError()
    _WndClassRuntimeData[classname] = (wndclass, finalMsgCBK)
    return wndclass

def UnregisterWindowClass(clsname: str) -> bool:
    success = bool(_user32.UnregisterClassW(clsname, 0))
    if success:
        _WndClassRuntimeData.pop(clsname, None)
    return success

def GetWindowClassInfo(classname: str) -> _wintype.WNDCLASSEXW:
    wndclass = _wintype.WNDCLASSEXW()
    _user32.GetClassInfoExW(_kernel32.GetModuleHandleW(0), classname, wndclass.ref)
    return wndclass

def IsWindowClassInSystem(classname: str) -> bool:
    return bool(_user32.GetClassInfoExW(0, classname, _wintype.WNDCLASSEXW().ref))
# endregion

# region ==> 创建窗口
# ==============================================================================================================
def CreateWindow(hparent: int, claname: str, title='', pos: _Pos=0, size: _Size=0, style=0, exstyle=0, lparam=0) -> int:
    if not pos: pos = _wincon.CW_USEDEFAULT, _wincon.CW_USEDEFAULT
    if not size: size = (50, 30) if style & _wincon.WS_CHILD else (_wincon.CW_USEDEFAULT, _wincon.CW_USEDEFAULT)
    hwnd = _user32.CreateWindowExW(exstyle, claname, title, style, *pos, *size, hparent, 0, 0, lparam)
    return hwnd

def CreateWindowAsync(looptid, hparent, clsname, title='', pos: _Pos=0, size: _Size=0, style=0, exstyle=0, lparam=0) -> int:
    hwnd = RequestMsgloopTask(CreateWindow, *locals().values())
    return hwnd
# endregion

# region ==> 渲染窗口
# ==============================================================================================================
def AddFontResource(fontpath: str) -> int:
    return _gdi32.AddFontResourceExW(fontpath, 0x10, 0)

def RemoveFontResource(fontpath: str) -> bool:
    return bool(_gdi32.RemoveFontResourceExW(fontpath, 0x10, 0))

def RedrawWindow(hwnd):
    _user32.RedrawWindow(hwnd,0,0,_wincon.RDW_ALLCHILDREN|_wincon.RDW_UPDATENOW|_wincon.RDW_FRAME|_wincon.RDW_INVALIDATE)

def InvalidateRect(hwnd):
    _user32.InvalidateRect(hwnd, GetClientRect(hwnd).ref, True)

def Paint(handle, text='', textcolor=0xffffff, textalign=(3,3), font='', fontsize=14, fillcolor=0x0):
    ps = _wintype.PAINTSTRUCT()
    hdc = _user32.BeginPaint(handle, ps.ref)
    _user32.FillRect(hdc, _ctypes.byref(ps.rcPaint), _gdi32.CreateSolidBrush(fillcolor))
    if str(text):
        xalign = (_wincon.DT_LEFT, _wincon.DT_RIGHT, _wincon.DT_CENTER)[textalign[0]-1]
        yalign = (_wincon.DT_TOP, _wincon.DT_BOTTOM, _wincon.DT_VCENTER)[textalign[1]-1]
        if font:
            hfont = _gdi32.CreateFontW(fontsize,0,0,0,400,0,0,0,0,0,0,0,0, font)
            _gdi32.SelectObject(hdc, hfont)
            _gdi32.DeleteObject(hfont)
        _gdi32.SetBkMode(hdc, -1)
        _gdi32.SetTextColor(hdc, textcolor)
        _user32.DrawTextW(hdc, str(text), -1, _ctypes.byref(ps.rcPaint), _wincon.DT_SINGLELINE|xalign|yalign)
    _user32.EndPaint(handle, ps.ref)
    _user32.ReleaseDC(handle, hdc)

def SetCapture(hwnd) -> int:
    return _user32.SetCapture(hwnd)

def ReleaseCapture() -> bool:
    return bool(_user32.ReleaseCapture())

def SetCursor(cursor: int | str) -> int:
    """可以是已加载的光标的句柄，也可以是以`IDC_`前缀的光标常量或者光标文件的路径"""
    if isinstance(cursor, str):
        cursor = _user32.LoadCursorFromFileW(cursor)
    previous_hcursor = _user32.SetCursor(cursor)
    if previous_hcursor == 0:
        _user32.SetCursor(_user32.LoadCursorW(0, cursor))
    return previous_hcursor

def SetWindowRound(hwnd, radius):
    rect = GetWindowRect(hwnd)
    hrgn = _gdi32.CreateRoundRectRgn(0, 0, *rect.size, radius, radius)
    _user32.SetWindowRgn(hwnd, hrgn, True)
    _gdi32.DeleteObject(hrgn)
# endregion

# region ==> 监听windows事件
# ==============================================================================================================
_WinEventHookRuntimeData = {}
def SetWinEventHook(
        callback, eventStart=_wincon.WM_APP, eventEnd=_wincon.WM_APPEND, inwindow=0, inprocess=0, inthread=0) -> int:
    # callback args: hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime
    if inwindow:
        inthread, inprocess = GetWindowThreadProcessId(inwindow)
    def wrappedcbk(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        if not inwindow or hwnd == inwindow:
            callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime)
    wineventproc = _wintype.WINEVENTPROC(wrappedcbk)
    hWinEventHook = _user32.SetWinEventHook(
        eventStart, eventEnd, 0, wineventproc, inprocess, inthread, _wincon.WINEVENT_OUTOFCONTEXT)
    if hWinEventHook:
        _WinEventHookRuntimeData[hWinEventHook] = wineventproc
    return hWinEventHook

def UnhookWinEvent(hEventHook) -> bool:
    success = bool(_user32.UnhookWinEvent(hEventHook))
    if success:
        _WinEventHookRuntimeData.pop(hEventHook, None)
    return success

def SetWinEventHookAsync(
        loopthreadid, callback,
        eventStart=_wincon.WM_APP, eventEnd=_wincon.WM_APPEND,
        inwindow=0, inprocess=0, inthread=0) -> int:
    return RequestMsgloopTask(SetWinEventHook, *locals().values())   # hEventHook

def UnhookWinEventAsync(loopthreadid, hEventHook) -> bool:
    return RequestMsgloopTask(UnhookWinEvent, *locals().values())    # success
# endregion

# region ==> 对话框
# ==============================================================================================================
def MessageBox(msg, title='提示', hownerwnd=0, top=False, utype: int=None) -> int:
    if utype is None:
        utype = _wincon.MB_OK | _wincon.MB_SETFOREGROUND | (_wincon.MB_SYSTEMMODAL if top else 0)
    return _user32.MessageBoxW(hownerwnd, str(msg), title, utype)

def AskFolder(msg: str='', default_path: str='', hownerwnd=0) -> str:
    default_path = _ctypes.create_unicode_buffer(default_path)
    # issue: 64位版本中，关闭项目的右键菜单时对话框意外停止
    def browseCallbackProc(hwnd, umsg, lparam, ldata):
        if umsg == _wincon.BFFM_INITIALIZED:
            SendMessage(hwnd, _wincon.BFFM_SETSELECTIONW, 1, _ctypes.addressof(default_path))
        return True
    browseinfo = _wintype.BROWSEINFOW()
    browseinfo.hwndOwner = hownerwnd
    browseinfo.lpszTitle = msg
    browseinfo.ulFlags = 1 | 0x40
    browseinfo.lpfn = _wintype.BFFCALLBACK(browseCallbackProc)
    pidl = _wintype.LPVOID(_shell32.SHBrowseForFolderW(browseinfo.ref))
    if pidl:
        pathbuffer = _ctypes.create_unicode_buffer(_wincon.MAX_PATH+1)
        _shell32.SHGetPathFromIDListW(pidl, _ctypes.byref(pathbuffer))
        _ole32.CoTaskMemFree(pidl)
        return _os.path.abspath(pathbuffer.value)
    return ''

def __AskFile(askfunc, hownerwnd=0, title='打开', initdir: str=..., initfname='', filter='All Files: *.*', *filters: str):
    """- filter 文件筛选器：'筛选器名称: 筛选表达式' 用例：'Python Files: *.py; *.pyc' 也可省略名称： '*.txt; *.png' """
    filters = ((p:=f.rpartition(':')) and f'{p[0]} ({p[2].strip()})\0{p[2]}\0' for f in (filter,) + filters)
    pathbuffer = _ctypes.create_unicode_buffer(_wincon.MAX_PATH+1)
    pathbuffer.value = initfname
    ofn = _wintype.OPENFILENAMEW()
    ofn.lStructSize = ofn.sizeof()
    ofn.hwndOwner = hownerwnd
    ofn.lpstrTitle = title
    ofn.lpstrInitialDir = None if initdir is ... else _os.path.abspath(initdir)
    ofn.lpstrFilter = ''.join(filters) + '\0'
    ofn.Flags = _wincon.OFN_EXPLORER | _wincon.OFN_FILEMUSTEXIST
    ofn.lpstrFile = _ctypes.cast(pathbuffer, _wintype.LPWSTR)
    ofn.nMaxFile = len(pathbuffer)
    return askfunc(ofn.ref) and _os.path.abspath(pathbuffer.value) or ''

def AskFile(hownerwnd=0, title='打开', initdir: str=..., filter='All Files: *.*', *filters: str):
    """- filter 文件筛选器：'筛选器名称: 筛选表达式' 用例：'Python Files: *.py; *.pyc' 也可省略名称： '*.txt; *.png' """
    return __AskFile(_comdlg32.GetOpenFileNameW, hownerwnd, title, initdir, '', filter, *filters)

def AskSaveFile(hownerwnd=0, title='另存为', initdir: str=..., initfname='', filter='All Files: *.*', *filters: str):
    """- filter 文件筛选器：'筛选器名称: 筛选表达式' 用例：'Python Files: *.py; *.pyc' 也可省略名称： '*.txt; *.png' """
    return __AskFile(_comdlg32.GetSaveFileNameW, hownerwnd, title, initdir, initfname, filter, *filters)
# endregion

# region ==> 注册表
# ==============================================================================================================
def RegOpenKey(kpath: str) -> int:
    root, subkpath = _os.path.relpath(kpath.lstrip('/').lstrip('\\')).split(_os.path.sep, 1)
    hKey = _ctypes.c_int(0)
    _advapi32.RegOpenKeyExW(
        getattr(_wincon, root.upper()),
        subkpath, 0,
        _wincon.KEY_ALL_ACCESS | _wincon.KEY_WOW64_64KEY,
        _ctypes.byref(hKey))
    return hKey.value

def RegCreateKey(kpath: str) -> int:
    root, subkpath = _os.path.relpath(kpath.lstrip('/').lstrip('\\')).split(_os.path.sep, 1)
    hKey = _ctypes.c_int(0)
    _advapi32.RegCreateKeyExW(
        getattr(_wincon, root.upper()),
        subkpath, 0, 0, 0,
        _wincon.KEY_ALL_ACCESS | _wincon.KEY_WOW64_64KEY, 0,
        _ctypes.byref(hKey), 0)
    return hKey.value

def RegCloseKey(hKey: int) -> int:
    error_code = _advapi32.RegCloseKey(hKey)
    return error_code

def IsRegKeyExist(kpath: str) -> bool:
    hk = RegOpenKey(kpath)
    RegCloseKey(hk)
    return bool(hk)

def CreateRegKey(kpath: str) -> bool:
    hk = RegCreateKey(kpath)
    success = bool(hk)
    RegCloseKey(hk)
    return success

def GetRegSubKeyNum(kpath: str) -> int:
    subkeynum = _ctypes.c_int(0)
    hk = RegOpenKey(kpath)
    _advapi32.RegQueryInfoKeyW(hk, 0, 0, 0, _ctypes.byref(subkeynum), *[0] * 8)
    RegCloseKey(hk)
    return subkeynum.value

def GetRegKeyTime(kpath: str, UTCdiff = +8) -> float:
    ftime = _wintype.FILETIME()
    systime = _wintype.SYSTEMTIME()
    hk = RegOpenKey(kpath)
    ret = _advapi32.RegQueryInfoKeyW(hk, *[0] * 10, ftime.ref)
    RegCloseKey(hk)
    _kernel32.FileTimeToSystemTime(ftime.ref, systime.ref)
    return ParseSYSTEMTIME(systime, UTCdiff)

def GetRegValue(kpath, valueName) -> str:
    size = 1024
    data = _ctypes.create_unicode_buffer(size)
    datasize = _ctypes.c_int(size)
    hk = RegOpenKey(kpath)
    ret = _advapi32.RegQueryValueExW(hk, valueName, 0, 0, _ctypes.byref(data), _ctypes.byref(datasize))
    RegCloseKey(hk)
    if ret == 0:
        return data.value

def SetRegValue(kpath: str, valueName: str, value: str):
    hk = RegOpenKey(kpath)
    data = _ctypes.create_unicode_buffer(value)
    datasize = _ctypes.sizeof(data)
    _advapi32.RegSetValueExW(hk, valueName, 0, _wincon.REG_SZ, data, datasize)
    RegCloseKey(hk)

def GetRegSubKeys(kpath):
    subkeys = []
    hk = RegOpenKey(kpath)
    subkeynum = _ctypes.c_int(0)
    subkeymaxsize = _ctypes.c_int(0)
    _advapi32.RegQueryInfoKeyW(hk, 0, 0, 0, _ctypes.byref(subkeynum), _ctypes.byref(subkeymaxsize), *[0] * 6)
    subkeymaxsize.value+=1
    for i in range(subkeynum.value):
        buf = _ctypes.create_unicode_buffer(subkeymaxsize.value)
        size = _ctypes.c_int(subkeymaxsize.value)
        _advapi32.RegEnumKeyExW(hk, i, _ctypes.byref(buf), _ctypes.byref(size), *[0]*4)
        subkeys.append(buf.value)
    RegCloseKey(hk)
    return subkeys
# endregion


def SetClipboardData(data: str):
    if not _user32.OpenClipboard(0):
        return
    _user32.EmptyClipboard()

    databytes = data.encode('utf-16le')
    datasize = len(databytes) + 2

    hMem = _kernel32.GlobalAlloc(_wincon.GMEM_MOVEABLE, datasize)
    if not hMem:
        _user32.CloseClipboard()
        return

    lpMem = _kernel32.GlobalLock(hMem)
    _ctypes.memmove(lpMem, databytes, datasize)
    _kernel32.GlobalUnlock(hMem)

    _user32.SetClipboardData(_wincon.CF_UNICODETEXT, hMem)
    _user32.CloseClipboard()
