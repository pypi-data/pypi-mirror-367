"""
RKGUIV3 - Comprehensive Tkinter-based GUI library
"""

# Основной импорт
try:
    from .core import GUIApp
    from .widgets import *
    from .dialogs import *
    from .utils import *
except ImportError as e:
    # Резервный импорт для отладки
    print(f"Import warning: {e}")
    try:
        from rkguiv3.core import GUIApp
        from rkguiv3.widgets import *
        from rkguiv3.dialogs import *
        from rkguiv3.utils import *
    except ImportError:
        raise ImportError("RKGUIV3 Error: Failed to import RKGUIV3 components")

__version__ = "0.1.4"
__author__ = "1001015dhh"
__license__ = "MIT"
