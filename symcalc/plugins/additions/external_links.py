from __future__ import annotations

import re as regex
import urllib
import webbrowser

from ...calc import Calculator
from ...plugin import CalculatorPlugin


class AddExternalLinks(CalculatorPlugin):
    """Calculator plugin to add external links to Desmos, Symbolab, Wolfram|Alpha and SymPy Gamma"""

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.desmos = self.desmos
        calc.context.symbolab = self.symbolab
        calc.context.wolframalpha = self.wolframalpha
        calc.context.sympygamma = self.sympygamma

    def desmos(self, expr=None) -> None:
        """Opens the Desmos graphing calculator in the browser. Available in the calculator context. Does not support passing on an expression"""
        webbrowser.open_new_tab("https://desmos.com/calculator")

    def symbolab(self, expr=None) -> None:
        """Opens Symbolab in the browser. Available in the calculator context"""
        webbrowser.open_new_tab("https://www.symbolab.com/" + (("solver/step-by-step/" + urllib.parse.quote(regex.sub("\*\s*\*", "^", str(expr)))) if expr is not None else ""))

    def wolframalpha(self, expr=None) -> None:
        """Opens Wolfram|Alpha in the browser. Available in the calculator context"""
        webbrowser.open_new_tab("https://www.wolframalpha.com/" + (f"input?i={expr}" if expr is not None else ""))
        # webbrowser.open_new_tab("https://www.wolframalpha.com/" + (("input?i=" + urllib.parse.quote(str(expr))) if expr is not None else ""))

    def sympygamma(self, expr=None) -> None:
        """Opens SymPy Gamma in the browser. Available in the calculator context"""
        webbrowser.open_new_tab("https://gamma.sympy.org/" + (f"input?i={expr}" if expr is not None else ""))
