import sys
from types import ModuleType

from ..plugin import CalculatorPlugin
from .additions import *
from .functionality import *
from .meta import *
from .notation import *
from .output import *
from .reminders import *
from .user import *

_plugins = None


def get_plugins():
    global _plugins
    if _plugins is None:
        _plugins = []
        for x in (self := sys.modules[__name__]).__dir__():
            if isinstance(m := self.__getattribute__(x), ModuleType):
                for c in m.__dir__():
                    t = m.__getattribute__(c)
                    if isinstance(t, type) and issubclass(t, CalculatorPlugin) and t != CalculatorPlugin:
                        _plugins.append(t)
    return _plugins
