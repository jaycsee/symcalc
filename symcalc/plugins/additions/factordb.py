from __future__ import annotations

from typing import Any

import requests
import sympy

from ...calc import Calculator
from ...plugin import CalculatorPlugin


class AddFactorDB(CalculatorPlugin):
    """Adds the API for FactorDB, a website that provides factors for numbers.

    .. code-block::

        Calculator >>> factordb(29928893193015398318666605389344864349536211)
        FactorDBResponse(29928893193015398318666605389344864349536211 is composite, fully factored)
            Factors: {3: 1, 11: 1, 648181: 1, 1399202008951362319095335248405636807: 1}

    The response object contains the number ``n`` queried, the ``status`` response, and ``factors`` as a :class:`dict`
    """

    class FactorDBResponse:
        definitions = {"C": "composite, no factors known", "CF": "composite, factors known", "FF": "composite, fully factored", "P": "prime", "Prp": "probably prime", "U": "unknown", "Unit": "1"}

        def __init__(self, n: int | str, json: dict[str, Any]):
            self.n = n
            self.status = json["status"]
            """The status of the queried number"""
            self.factors = {}
            """The factors of the queried number"""
            for k, v in json["factors"]:
                self.factors[sympy.sympify(k)] = sympy.sympify(v)

        def __str__(self) -> str:
            return self.__repr__()

        def __repr__(self) -> str:
            return f"FactorDBResponse({self.n} is {self.definitions[self.status]})\nFactors: {self.factors}"

    def __init__(self):
        super().__init__(self.__class__.__name__, -1)

    def hook(self, calc: Calculator) -> None:
        """Updates the calculator context"""
        calc.context.factordb = self.factordb

    def factordb(self, n: int | str) -> AddFactorDB.FactorDBResponse:
        """Get the response from FactorDB

        Parameters
        ----------
        n : int | str
            The number to query

        Returns
        -------
        :class:`AddFactorDB.FactorDBResponse`
            The response from FactorDB
        """
        return AddFactorDB.FactorDBResponse(n, requests.get("http://factordb.com/api", params={"query": str(n)}).json())
