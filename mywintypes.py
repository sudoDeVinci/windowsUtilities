from typing import TypedDict, Union, Any

# Command object variants (many fields optional)
CommandDict = TypedDict(
    "CommandDict",
    {
        "action": str,
        "name": str,
        "dropdownDuration": int,
        "toggleVisibility": bool,
        "monitor": str,
        "desktop": str,
        "singleLine": bool,
        "split": str,
        "splitMode": str,
    },
    total=False,
)

# Single action entry
ActionEntry = TypedDict(
    "ActionEntry",
    {
        "command": Union[str, CommandDict],
        "id": str,
        "keys": str,
    },
    total=False,
)

# Font inside profile defaults
Font = TypedDict(
    "Font",
    {
        "face": str,
        "size": int,
    },
    total=False,
)

# Profile defaults
ProfileDefaults = TypedDict(
    "ProfileDefaults",
    {
        "background": str,
        "colorScheme": str,
        "font": Font,
        "opacity": int,
        "useAcrylic": bool,
    },
    total=False,
)

# Individual profile item
ProfileItem = TypedDict(
    "ProfileItem",
    {
        "closeOnExit": str,
        "elevate": bool,
        "guid": str,
        "hidden": bool,
        "name": str,
        "source": str,
        "font": Font,
    },
    total=False,
)

# Profiles container
Profiles = TypedDict(
    "Profiles",
    {
        "defaults": ProfileDefaults,
        "list": list[ProfileItem],
    },
    total=False,
)

# newTabMenu entry
NewTabEntry = TypedDict("NewTabEntry", {"type": str}, total=False)

# Color scheme entry (most fields optional)
Scheme = TypedDict(
    "Scheme",
    {
        "name": str,
        "background": str,
        "black": str,
        "blue": str,
        "brightBlack": str,
        "brightBlue": str,
        "brightCyan": str,
        "brightGreen": str,
        "brightPurple": str,
        "brightRed": str,
        "brightWhite": str,
        "brightYellow": str,
        "cursorColor": str,
        "cyan": str,
        "foreground": str,
        "green": str,
        "purple": str,
        "red": str,
        "selectionBackground": str,
        "white": str,
        "yellow": str,
    },
    total=False,
)

# 
TerminalSettingMap = TypedDict(
    "TerminalSettingMap",
    {
        "$help": str | None,
        "$schema": str | None,
        "actions": list[ActionEntry],
        "alwaysShowNotificationIcon": bool,
        "copyFormatting": str,
        "copyOnSelect": bool,
        "defaultProfile": str,
        "firstWindowPreference": str,
        "launchMode": str,
        "newTabMenu": list[NewTabEntry],
        "profiles": Profiles,
        "schemes": list[Scheme],
        "showTabsInTitlebar": bool,
        "startOnUserLogin": bool,
        "themes": list[Any],
        "useAcrylicInTabRow": bool,
        "windowingBehavior": str,
        "initialCols": int | None,
        "initialRows": int | None,
    },
    total=False
)