import code
from typing import Any, Callable

import sympy
from symcalc import CalculatorContext

from tests import random_str


def get_context_value(context: CalculatorContext, value: str, assert_cmp: Callable[[Any, Any], bool]):
    r = context.__dict__[value]
    assert assert_cmp(r, context.__getattribute__(value))
    return r


def test_context_instantiate():
    context = CalculatorContext()

    assert context.sympy is sympy
    for x in sympy.__dict__:
        assert x in context.__dict__


def test_context_use_exec():
    context = CalculatorContext()

    names = [random_str() for i in range(5)]

    exec("x = 0", context.__dict__, context.__dict__)
    exec(f"{names[0]} = 3", context.__dict__, context.__dict__)
    exec(f"{names[1]} = 3", context.__dict__, context.__dict__)
    exec(f"class {names[2]}: pass", context.__dict__, context.__dict__)
    exec(f"{names[3]} = {names[2]}()", context.__dict__, context.__dict__)
    exec(f"{names[4]} = {names[3]}", context.__dict__, context.__dict__)

    cmp_eq = lambda a, b: a == b
    cmp_is = lambda a, b: a is b

    assert context.x == get_context_value(context, "x", cmp_eq) == 0
    assert get_context_value(context, names[0], cmp_eq) == get_context_value(context, names[1], cmp_eq) == 3
    assert isinstance(get_context_value(context, names[2], cmp_is), type)
    assert isinstance(get_context_value(context, names[3], cmp_is), get_context_value(context, names[2], cmp_is))
    assert get_context_value(context, names[3], cmp_is) is get_context_value(context, names[4], cmp_is)


def test_context_use_console():
    context = CalculatorContext()
    console = code.InteractiveConsole(context.__dict__)

    names = [random_str() for i in range(5)]

    console.push("x = 0")
    console.push(f"{names[0]} = 3")
    console.push(f"{names[1]} = 3")
    console.push(f"class {names[2]}: pass\n")
    console.push(f"{names[3]} = {names[2]}()")
    console.push(f"{names[4]} = {names[3]}")

    cmp_eq = lambda a, b: a == b
    cmp_is = lambda a, b: a is b

    assert context.x == get_context_value(context, "x", cmp_eq) == 0
    assert get_context_value(context, names[0], cmp_eq) == get_context_value(context, names[1], cmp_eq) == 3
    assert isinstance(get_context_value(context, names[2], cmp_is), type)
    assert isinstance(get_context_value(context, names[3], cmp_is), get_context_value(context, names[2], cmp_is))
    assert get_context_value(context, names[3], cmp_is) is get_context_value(context, names[4], cmp_is)
