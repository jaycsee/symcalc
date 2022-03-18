import sympy


class CalculatorContext:
    """Contains all of the available methods and variables in a class. CalculatorContext.__dict__ works similarly to globals()"""

    def __init__(self) -> None:
        """Initializes the default calculator context"""
        self.__dict__["sympy"] = sympy
        self.__dict__.update(sympy.__dict__)
        self.plot_3d = sympy.plotting.plot3d
