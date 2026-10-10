"""System-DPI awareness for Windows/Tk 8.6, without bitmap virtualization."""
import ctypes


def enable_dpi_awareness():
    # Set before creating any Tk window. Packaged EXE also declares this mode.
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


def system_dpi():
    try:
        dpi = ctypes.windll.user32.GetDpiForSystem()
        return dpi if dpi > 0 else 96
    except (AttributeError, OSError):
        return 96
