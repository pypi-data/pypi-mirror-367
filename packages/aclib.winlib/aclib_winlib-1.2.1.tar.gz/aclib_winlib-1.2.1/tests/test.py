from aclib.winlib import winapi

winapi.SetWindowTopMost(265966, True)
print(winapi.IsWindowTopMost(265966))