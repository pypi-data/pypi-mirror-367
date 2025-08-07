import json
import importlib.resources
from .monitor_dll import MonitorInfoDLL

class MonitorCollector:
    def __init__(self):
        # Usa importlib.resources para obter o caminho da DLL embutida no pacote
        with importlib.resources.path("diixscreendata.dll", "Dix_ScreenInfo.dll") as dll_path:
            self.dll = MonitorInfoDLL(str(dll_path))

    def collect(self):
        monitors = self.dll.get_monitors()
        all_data = []

        for mon in monitors:
            modes = self.dll.get_supported_modes(mon.deviceName)

            monitor_data = {
                "deviceName": mon.deviceName,
                "resolution": f"{mon.width}x{mon.height}",
                "maxWindowSize": (mon.maxWindowWidth, mon.maxWindowHeight),
                "minWindowSize": (mon.minWindowWidth, mon.minWindowHeight),
                "frequency": mon.frequency,
                "bitsPerPel": mon.bitsPerPel,
                "orientation": mon.orientation,
                "isAttached": mon.isAttached,
                "isPrimary": mon.isPrimary,
                "isFocused": mon.isFocused,
                "position": (mon.posX, mon.posY),
                "center": (mon.centerX, mon.centerY),
                "supportedModes": sorted(
                    {f"{mode.width}x{mode.height}" for mode in modes},
                    key=lambda x: (int(x.split('x')[0]), int(x.split('x')[1]))
                ),
            }

            all_data.append(monitor_data)

        return all_data
