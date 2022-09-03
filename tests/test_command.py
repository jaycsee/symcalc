import ast

import pytest
from symcalc import Calculator, CalculatorCommand

from tests import random_str


def test_command_instantiate():
    calc = Calculator()
    command = CalculatorCommand(calc, c := random_str())

    assert command.calc is calc
    assert command._command == c
    assert command._command_ast is None
    assert command._command_symtable is None
    assert not command._valid_syntax
    assert not command.multiline_command
    assert command.buffer is None
    assert not command.abort
    assert not command.resend_command
    assert not command.print_error
    assert not command.success


def test_command_get_set_command():
    calc = Calculator()
    command = CalculatorCommand(calc, c := random_str())
    assert command.command == command._command == c
    command.command = c = random_str()
    assert command.command == command._command == c


def test_command_ast():
    calc = Calculator()
    command = CalculatorCommand(calc, c := random_str())
    command.command = "invalid command"
    command.command = c
    command.valid_syntax = True
    found = False
    for node in ast.walk(command.command_ast):
        if isinstance(node, ast.Name) and node.id == c:
            found = True
    assert found
    command.command = c = random_str()
    found = False
    for node in ast.walk(command.command_ast):
        if isinstance(node, ast.Name) and node.id == c:
            found = True
    assert found
    with pytest.raises(SyntaxError):
        command.command = f"{random_str()} {random_str()}"


def test_command_ast_set():
    calc = Calculator()
    command = CalculatorCommand(calc, f"[{', '.join(random_str() for i in range(10))}]")
    command.valid_syntax = True

    class Transformer(ast.NodeTransformer):
        def visit_Name(self, node):
            return ast.Constant(1)

    command.command_ast = ast.fix_missing_locations(Transformer().visit(command.command_ast))
    assert ast.literal_eval(command.command_ast.body[0].value) == [1] * 10


def test_command_ast_invalid():
    calc = Calculator()
    command = CalculatorCommand(calc, f"{random_str()} {random_str()}")
    with pytest.raises(ValueError):
        command.command_ast


def test_command_symtable():
    calc = Calculator()
    names_ast = set([random_str() for i in range(10)])
    names_sym = names_ast.copy()
    command = CalculatorCommand(calc, f"({', '.join(names_ast)})")
    command.valid_syntax = True
    for node in ast.walk(command.command_ast):
        if isinstance(node, ast.Name):
            names_ast.remove(node.id)
    assert not names_ast
    for name in command.command_symtable.get_symbols():
        names_sym.remove(name.get_name())
    assert not names_sym


def test_command_symtable_invalid():
    calc = Calculator()
    command = CalculatorCommand(calc, f"{random_str()} {random_str()}")
    with pytest.raises(ValueError):
        command.command_symtable


def test_command_str():
    calc = Calculator()
    command = CalculatorCommand(calc, c := random_str())
    assert str(command) == c


def test_command_repr():
    calc = Calculator()
    command = CalculatorCommand(calc, c := random_str())
    assert c in repr(command)
