from __future__ import annotations

from .calc import *
from .plugins.plugins_additions import *
from .plugins.plugins_functionality import *
from .plugins.plugins_meta import *
from .plugins.plugins_notation import *
from .plugins.plugins_output import *
from .plugins.plugins_reminders import *


class DefaultCalculator(Calculator):
    """A :class:`Calculator` that contains the default environment.
    Running the module is equivalent to

    >>> import symcalc
    >>> symcalc.DefaultCalculator().register_default_plugins().interact("Demo")
    Demo >>>
    """

    def __init__(self, *args, **kwargs):
        """Initializes the calculator. See :class:`Calculator`

        .. note:: This does **NOT** automatically register the default plugins. Call :meth:`register_default_plugins`
        """
        super().__init__(*args, **kwargs)
        self.registered = False

    def register_default_plugins(self) -> DefaultCalculator:
        """Registers the default plugins.

        Returns
        -------
        :class:`DefaultCalculator`
            Returns ``self`` for chaining
        """
        self.registered = True
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

    def interact(self, *args, **kwargs):
        """See :meth:`Calculator.interact`"""
        if not self.registered:
            print("The default plugins were not regstered. Did you mean to use the Calculator class or forget to call register_default_plugins()?")
        super().interact(*args, **kwargs)
