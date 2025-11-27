from sys import (
    executable as sys_executable,
    argv as sys_argv,
    exit as sys_exit
)
from os import path
from  json import (
    dump as json_dump,
    load as json_load
)
import winreg
from typing import cast
from pathlib import Path
from ctypes import windll
from mywintypes import TerminalSettingMap
import pywintypes
import win32api
import win32con


StatusTuple = tuple[bool, Exception | None]


def is_admin() -> StatusTuple:
    """
    Check if the current process has administrator privileges.
    Returns:
        (tuple[bool, Exception]): Whether or not the current user is admin, and associated error if any
    """
    try:
        return (windll.shell32.IsUserAnAdmin(), None)
    except Exception as e:
        return (False, e)


def run_as_admin() -> None:
    """
    Re-run the current script with administrator privileges.
    We want to fail fast here and propagate the errors upward.
    """
    ia, _ = is_admin()
    if not ia:
        windll.shell32.ShellExecuteW(
            None, "runas", sys_executable, " ".join(sys_argv), None, 1
        )

        # Always exit the non-elevated process after requesting elevation
        sys_exit(0)


def get_display_resolution() -> tuple[int, int]:
    """
    Get the current display resolution.
    Returns:
        tuple[int, int]: Second item is the dimensions in the form (width, height).
    Raises:
        Exception: Any number os OS errors; catch generally.
    """
    user32 = windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return (width, height)


def set_display_resolution(target: tuple[int, int]) -> StatusTuple:
    """
    Set the display resolution to 1360x768.
    Note: This may not work on all systems and may require admin privileges.
    Args:
        target (tuple[int, int]): target resolution in the form (width, height)
    Return:
        (tuple[bool, Exception | None]): whether the operation was a success, and related Exception if applicable.
    """

    try:
        res = get_display_resolution()

        if res == target:
            return(True, None)
        
        ia, _ = is_admin()
        if not ia:
            run_as_admin()

        devmode = pywintypes.DEVMODEType()
        devmode.PelsWidth = 1360
        devmode.PelsHeight = 768
        devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
        result = win32api.ChangeDisplaySettings(devmode, 0)
        if result != win32con.DISP_CHANGE_SUCCESSFUL:
            raise Exception("No specifics given")
    except Exception as e:
        return (False, e)
    
    return (True, None)


def add_to_windows_path(new_path: Path) -> StatusTuple:
    """
    Add a directory to the system PATH environment variable permanently.
    Args:
        new_path (Path): path to add to the system PATH environment variable.
    Return:
        (tuple[bool, Exception | None]): whether the operation was a success, and related Exception if applicable.
    """

    try:

        ia, _ = is_admin()
        if not ia:
            not run_as_admin()

        if not new_path.exists():
            raise Exception(f"{new_path} does not exist")

        # The registry key for system environment variables
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            0,
            winreg.KEY_ALL_ACCESS,
        ) as key:

            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""

            # Check if path is already in PATH
            # PATH is a semicolon-separated-value string of paths
            current_path.strip(";")
            path_entries = current_path.split(";")
            for i in range(len(path_entries)):
                print(f"> {i}: {path_entries[i]}")
            new_path_str = str(new_path)

            if new_path_str in path_entries:
                return (True, None)
            
            updated_path = f"{current_path};{new_path_str}"

            # Set the new PATH value
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, updated_path)
            return (True, None)

    except Exception as e:
        return (False, e)


def change_terminal_settings(new_settings: TerminalSettingMap) -> StatusTuple:
    """
    Change various settings in the new windows terminal.
    """

    try:

        # Path to the Windows Terminal settings file
        settingFile = Path(
            path.expandvars(
                r"%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
            )
        )

        if not settingFile.exists():
            raise FileNotFoundError(f"Terminal setting file not found at path {settingFile}")

        # We open the file twice here instead of using r+ mode to avoid issues with the file size
        # We read the entire file, modify it in memory, then write it back
        # This is simpler and less error-prone for JSON files

        with open(settingFile, "r", encoding="utf-8") as f:
            settings: TerminalSettingMap = cast(TerminalSettingMap, json_load(f))
        
        settings.update(new_settings)

        with open(settingFile, "w", encoding="utf-8") as f:
            json_dump(settings, f, indent=4)

    except Exception as e:
        return (False, e)
    
    return (True, None)


def change_cmd_font() -> None:
    """
    Change the Command Prompt (cmd.exe) console font size via registry.
    This affects the traditional cmd.exe windows, not Windows Terminal.
    """
    if not is_admin():
        run_as_admin()
        
    try:
        # Registry path for console settings
        console_key_path = r"Console"
        
        # Open or create the registry key
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, console_key_path) as key:
            # Font size is stored as a DWORD where:
            # - High word (upper 16 bits) = font height in pixels
            # - Low word (lower 16 bits) = font width (usually 0 for auto)
            # For size 14 font, height = 14 pixels (0x0E)
            font_size = 0x000E0000  # 14 pixels in the high word
            winreg.SetValueEx(key, "FontSize", 0, winreg.REG_DWORD, font_size)
            # Also set the font family to a smaller raster font
            winreg.SetValueEx(key, "FontFamily", 0, winreg.REG_DWORD, 0x00000036)
            # Set font weight to normal (400)
            winreg.SetValueEx(key, "FontWeight", 0, winreg.REG_DWORD, 400)
            print("Command Prompt font size updated to 16 pixels.")
            
    except Exception as e:
        print(f"Error modifying cmd.exe font settings: {e}")
