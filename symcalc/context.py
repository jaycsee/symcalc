import sympy


class CalculatorContext:
    """Contains all of the available methods and variables for a :class:`Calculator`. The attribute :attr:`CalculatorContext.__dict__` is meant to emulate :func:`globals()`"""

    def __init__(self):
        """Initializes the default calculator context"""
        self.__dict__["sympy"] = sympy
        self.__dict__.update(sympy.__dict__)
