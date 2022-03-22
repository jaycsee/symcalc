from __future__ import annotations

import importlib
import os

from . import plugins
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

    Examples
    --------

    .. code-block::

        Calculator >>> solve(x**2+4x-7)
        New symbol: x
        [-2 + √11, -√11 - 2]
        Decimals: [1.3166, -5.3166]
        Result stored in out[1]

        Calculator >>> solveset(sin(x))
        {2⋅n⋅π │ n ∊ ℤ} ∪ {2⋅n⋅π + π │ n ∊ ℤ}
        Result stored in out[2]

        Calculator >>> diff(2x**2sin(x))
        2
        2⋅x ⋅cos(x) + 4⋅x⋅sin(x)
        Result stored in out[3]

        Calculator >>> _.subs(x, 3)
        18⋅cos(3) + 12⋅sin(3)
        Decimal: -16.1264248420896
        Result stored in out[4]

        Calculator >>> integrate(sin(x)**2, (x,0,2))
        sin(2)⋅cos(2)
        - ───────────── + 1
                2
        Decimal: 1.18920062382698
        Result stored in out[5]

        Calculator >>> v[1,2,3]+v[4,5,6]
        ⎡5⎤
        ⎢ ⎥
        ⎢7⎥
        ⎢ ⎥
        ⎣9⎦
        Result stored in out[6]

        Calculator >>> m[1,2,3\\3,2,1\\5,5,9]
        ⎡1  2  3⎤
        ⎢       ⎥
        ⎢3  2  1⎥
        ⎢       ⎥
        ⎣5  5  9⎦
        Result stored in out[7]

        Calculator >>> _.det()
        -16
        Result stored in out[8]

        Calculator >>> out[7]*out[6]
        ⎡46 ⎤
        ⎢   ⎥
        ⎢38 ⎥
        ⎢   ⎥
        ⎣141⎦
        Result stored in out[9]
    """

    def __init__(self, *args, **kwargs):
        """Initializes the calculator. See :class:`Calculator`

        .. note:: This does **NOT** automatically register the default plugins. Call :meth:`register_default_plugins`
        """
        super().__init__(*args, **kwargs)
        self.registered = False
        self.defaultplugins = []

        for x in [f for f in plugins.__dir__() if f.startswith("plugins_")]:
            m = importlib.import_module(f".{x}", "symcalc.plugins")
            for c in m.__dir__():
                if isinstance(t := m.__getattribute__(c), type(DefaultCalculator)) and issubclass(t, CalculatorPlugin) and t != CalculatorPlugin:
                    self.defaultplugins.append(t)

    def register_default_plugins(self) -> DefaultCalculator:
        """Registers the default plugins.

        Returns
        -------
        :class:`DefaultCalculator`
            Returns ``self`` for chaining
        """
        self.registered = True
        for p in self.defaultplugins:
            self.register_plugin(p())
        return self

    def interact(self, *args, **kwargs):
        """See :meth:`Calculator.interact`"""
        if not self.registered:
            print("The default plugins were not regstered. Did you mean to use the Calculator class or forget to call register_default_plugins()?")
        super().interact(*args, **kwargs)
