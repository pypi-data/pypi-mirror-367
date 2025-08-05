from bear_utils.graphics.font._utils import ascii_header

from ._typing_stuff import ObjectTypeError, type_param, validate_type
from .clipboard import (
    ClipboardManager,
    clear_clipboard,
    clear_clipboard_async,
    copy_to_clipboard,
    copy_to_clipboard_async,
    paste_from_clipboard,
    paste_from_clipboard_async,
)
from .platform_utils import (
    DARWIN,
    LINUX,
    OS,
    OTHER,
    WINDOWS,
    get_platform,
    is_linux,
    is_macos,
    is_windows,
)

__all__ = [
    "DARWIN",
    "LINUX",
    "OS",
    "OTHER",
    "WINDOWS",
    "ClipboardManager",
    "ObjectTypeError",
    "ascii_header",
    "clear_clipboard",
    "clear_clipboard_async",
    "copy_to_clipboard",
    "copy_to_clipboard_async",
    "get_platform",
    "is_linux",
    "is_macos",
    "is_windows",
    "paste_from_clipboard",
    "paste_from_clipboard_async",
    "type_param",
    "validate_type",
]
