try:
    # Стандартный импорт
    from .core import GUIApp
    from .widgets import *
    from .dialogs import *
    from .utils import *
except ImportError:
    # Резервный вариант для случаев, когда пакет не установлен
    from core import GUIApp
    from widgets import *
    from dialogs import *
    from utils import *

__version__ = "0.1.2"
__author__ = "1001015dhh"
__license__ = "MIT"