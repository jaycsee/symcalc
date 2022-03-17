from __future__ import annotations

from .calc import *
from .plugins_additions import *
from .plugins_functionality import *
from .plugins_meta import *
from .plugins_notation import *
from .plugins_output import *
from .plugins_reminders import *


class DefaultCalculator(Calculator):
    def register_default_plugins(self) -> DefaultCalculator:
        """Register the default plugins. Returns itself for chaining"""
        defaultplugins = [
            PerformanceMonitor,
            PrintCommand,
            AddCisFunction,
            AddExternalLinks,
            AddnIntegrate,
            AddNewtonsMethod,
            AddOriginVectors,
            NotationConstants,
            NotationExponent,
            AutoExact,
            NotationInterval,
            NotationMultiply,
            AutoSymbol,
            NotationVector,
            OutputDecimal,
            OutputStore,
            ReminderMathConstants,
            ReminderTwoLetterSymbol,
        ]
        for p in defaultplugins:
            self.register_plugin(p())
        return self
