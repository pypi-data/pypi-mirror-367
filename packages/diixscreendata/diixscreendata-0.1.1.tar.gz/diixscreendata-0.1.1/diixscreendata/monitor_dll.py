import ctypes
import os

class MonitorInfo(ctypes.Structure):
    _fields_ = [
        ("deviceName", ctypes.c_wchar * 32),
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("maxWindowWidth", ctypes.c_int),
        ("maxWindowHeight", ctypes.c_int),
        ("minWindowWidth", ctypes.c_int),
        ("minWindowHeight", ctypes.c_int),
        ("frequency", ctypes.c_int),
        ("bitsPerPel", ctypes.c_int),
        ("orientation", ctypes.c_int),
        ("isAttached", ctypes.c_bool),
        ("isPrimary", ctypes.c_bool),
        ("isFocused", ctypes.c_bool),
        ("posX", ctypes.c_int),
        ("posY", ctypes.c_int),
        ("centerX", ctypes.c_int),
        ("centerY", ctypes.c_int),
    ]

class DisplayMode(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("frequency", ctypes.c_int),
        ("bitsPerPel", ctypes.c_int),
        ("orientation", ctypes.c_int),
    ]

class MonitorInfoDLL:
    def __init__(self, dll_path: str):
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Arquivo DLL não encontrado: {dll_path}")

        self.dll = ctypes.WinDLL(dll_path)

        self.dll.GetMonitorInfoList.argtypes = [ctypes.POINTER(MonitorInfo), ctypes.c_int]
        self.dll.GetMonitorInfoList.restype = ctypes.c_int

        self.dll.GetSupportedDisplayModes.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(DisplayMode), ctypes.c_int]
        self.dll.GetSupportedDisplayModes.restype = ctypes.c_int

    def get_monitors(self, max_monitors=16):
        buffer = (MonitorInfo * max_monitors)()
        count = self.dll.GetMonitorInfoList(buffer, max_monitors)
        return buffer[:count]

    def get_supported_modes(self, device_name, max_modes=100):
        buffer = (DisplayMode * max_modes)()
        count = self.dll.GetSupportedDisplayModes(device_name, buffer, max_modes)
        return buffer[:count]
