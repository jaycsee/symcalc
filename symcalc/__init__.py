"""SymCalc is a symbolic calculator built purely in Python on top of the SymPy library. """

from .calc import Calculator
from .command import CalculatorCommand
from .context import CalculatorContext
from .defaultcalc import DefaultCalculator
from .plugin import CalculatorPlugin


def use():
    DefaultCalculator().register_default_plugins().interact()
