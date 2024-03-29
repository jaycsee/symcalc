from __future__ import annotations

import sys
import warnings

from . import plugins
from .calc import *


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
        self.defaultplugins = plugins.get_plugins()

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
        if sys.version_info[0] < 3 or sys.version_info[1] < 10:
            warnings.warn(f"The default calculator is only tested to work on Python 3.10. You are currently running version {sys.version_info[0]}.{sys.version_info[1]}")
        if "set_int_max_str_digits" in dir(sys):
            sys.set_int_max_str_digits(0)
        if not self.registered:
            warnings.warn("The default plugins were not regstered. Did you mean to use the Calculator class or forget to call register_default_plugins()?")
        warnings.filterwarnings("ignore", ".*object is not subscriptable; perhaps you missed a comma?")
        warnings.filterwarnings("ignore", ".*object is not callable; perhaps you missed a comma?")
        super().interact(*args, **kwargs)
