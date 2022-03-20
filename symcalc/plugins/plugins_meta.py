from __future__ import annotations

import time
from typing import Any

from sympy import *

from ..calc import Calculator
from ..command import CalculatorCommand
from ..plugin import CalculatorPlugin


class PrintCommand(CalculatorPlugin):
    """Calculator plugin to print the resulting command after processing to stdout

    With the default plugin :class:`AutoExact` enabled:

    .. code-block::

        Calculator >>> /pc
        Calculator >>> 1.2
        Parsed Command: 1.2
        Handled Command: sympify('1.2', rational=True)
        6/5
        Calculator >>> 324.12
        Parsed Command: 324.12
        Handled Command: sympify('324.12', rational=True)
        8103
        ────
         25

    """

    def __init__(self):
        super().__init__(self.__class__.__name__, 999)
        self.settings_name = "print_command"
        self.settings_toggle = "pc"

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = False
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name

    def parse_command(self, command: CalculatorCommand) -> None:
        """Prints the command if the setting is set"""
        if not command.calc.settings[self.settings_name]:
            return
        print(f"Parsed Command: {command.command}")

    def handle_command(self, command: CalculatorCommand) -> None:
        """Prints the command if the setting is set"""
        if not command.calc.settings[self.settings_name]:
            return
        print(f"Handled Command: {command.command}")

    def handle_resend(self, command: CalculatorCommand) -> None:
        """Prints the command if the setting is set"""
        if not command.calc.settings[self.settings_name]:
            return
        print(f"Resent command: {command.command}")


class PerformanceMonitor(CalculatorPlugin):
    """Calculator plugin to profile the performance of the plugins installed

    With the default plugin :class:`AutoExact` enabled:

    .. code-block::

        Calculator >>> /pp
        Calculator >>> 1.2
        ----------[ Output ]----------
        6/5
        Decimal: 1.20000000000000
        Result stored in out[1]
        ----------[ Performance ]----------
        Events:
        - Parsing `1.2`
        - Handling `1.2`
        - Executing `sympify('1.2', rational=True)`
        - Successfully executed command
        Profile:
        - Command parsing took 0.0 ns
        - Command handling took 0.51 ms
        - Command execution took 1.5 ms
        - Success handling took 1.52 ms
        Calculator >>> 324.12
        ----------[ Output ]----------
        8103
        ────
         25
        ----------[ Performance ]----------
        Events:
        - Parsing `324.12`
        - Handling `324.12`
        - Executing `sympify('324.12', rational=True)`
        - Successfully executed command
        Profile:
        - Command parsing took 0.497 ms
        - Command handling took 0.519 ms
        - Command execution took 1.51 ms
        - Success handling took 0.991 ms

    """

    class PerformanceEvent:
        """Data class to log the data of a single event"""

        def __init__(self, time_name: str, event_name: str):
            self.time_name = time_name
            self.event_name = event_name
            self.command = None
            self.start_time = -1
            self.end_time = -1
            self.duration = -1
            self.time_phrase = " took "

        def start(self) -> None:
            """Starts the event, logging the time"""
            self.start_time = time.time_ns()

        def end(self) -> None:
            """Ends the event, logging the time"""
            self.end_time = time.time_ns()
            self.duration = self.end_time - self.start_time

        def get_duration(self) -> int:
            """Returns the duration of the event, in ns"""
            return self.duration

        def get_duration_str(self) -> str:
            """Returns a formated duration of the event as a str"""
            dur = self.get_duration()
            unit = "ns"
            if dur >= 100:
                dur /= 1000
                unit = "us"
            if dur >= 100:
                dur /= 1000
                unit = "ms"
            if dur >= 100:
                dur /= 1000
                unit = "s"
            dur /= 1.0
            return f"{dur:.3} {unit}"

        def get_time_str(self) -> str:
            """Returns the formatted duration of the event as a sentence"""
            return f"{self.time_name}{self.time_phrase}{self.get_duration_str()}"

        def get_event_str(self):
            """Returns the event name"""
            return self.event_name

    class PerformanceProfile:
        """Data class to store the events of a calculator command"""

        def __init__(self):
            self.clear()

        def start_event(self, *args, **kwargs) -> PerformanceMonitor.PerformanceEvent:
            """Starts an event. See the constructor of PerformanceMonitor.PerformanceEvent for arguments. Returns the event"""
            self.active_event = PerformanceMonitor.PerformanceEvent(*args, **kwargs)
            self.active_event.start()
            return self.active_event

        def end_event(self) -> bool:
            """Ends the active event. Returns whether an event was ended"""
            if self.active_event is None:
                return False
            self.active_event.end()
            self.event_list.append(self.active_event)
            self.active_event = None
            return True

        def abort_event(self) -> bool:
            """Aborts the active event. Returns whether an event was aborted"""
            if self.active_event is None:
                return False
            self.active_event.end()
            self.active_event.time_phrase = " aborted after "
            self.event_list.append(self.active_event)
            self.active_event = None
            return True

        def die_event(self) -> bool:
            """Kills the active event. Returns whether an event was killed"""
            if self.active_event is None:
                return False
            self.active_event.end()
            self.active_event.time_phrase = " died after "
            self.event_list.append(self.active_event)
            self.active_event = None
            return True

        def clear(self) -> None:
            """Clears the event list"""
            self.active_event = None
            self.event_list = []

        def print(self) -> None:
            """Prints the log of events and the performance profile"""
            print("----------[ Performance ]----------")
            print("Events:")
            for e in self.event_list:
                print(f" - {e.get_event_str()}")
            print("Profile:")
            for e in self.event_list:
                print(f" - {e.get_time_str()}")

    class PerformanceMonitorHelper(CalculatorPlugin):
        """Helper plugin for PerformanceMonitor"""

        def __init__(self, profile: PerformanceMonitor.PerformanceProfile, settings_key: str):
            super().__init__(self.__class__.__name__, 9999)
            self.profile = profile
            self.settings_key = settings_key

        def parse_command(self, command: CalculatorCommand) -> None:
            """Executed after all of the command parsing is complete"""
            self.profile.end_event()

        def handle_command(self, command: CalculatorCommand) -> None:
            """Executed after all of the command handling is complete"""
            self.profile.end_event()
            self.profile.start_event("Command execution", f"Executing `{command.command}`")

        def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
            """Executed after all of the runtime error handling is complete"""
            self.profile.end_event()

        def handle_syntax_error(self, command: CalculatorCommand, data: str) -> None:
            """Executed after all of the syntax error handling is complete"""
            self.profile.end_event()

        def handle_resend(self, command: CalculatorCommand) -> None:
            """Executed after all of the resend parsing is complete"""
            self.profile.end_event()
            self.profile.start_event("Resend execution", f"Executing `{command.command}`")

        def command_success(self, command: CalculatorCommand) -> None:
            """Executed after all of the success handling is complete"""
            self.profile.end_event()
            if command.calc.settings[self.settings_key]:
                self.profile.print()

        def command_fail(self, command: CalculatorCommand) -> None:
            """Executed after all of the failure handling is complete"""
            self.profile.end_event()
            if command.calc.settings[self.settings_key]:
                self.profile.print()

    def __init__(self):
        super().__init__(self.__class__.__name__, 0)
        self.settings_name = "performance_monitor"
        self.settings_toggle = "pp"
        self.settings_toggle2 = "pm"
        self.profile = PerformanceMonitor.PerformanceProfile()
        self.helper = PerformanceMonitor.PerformanceMonitorHelper(self.profile, self.settings_name)

    def hook(self, calc: Calculator) -> None:
        """Sets the settings in the calculator to their default values"""
        calc.settings[self.settings_name] = False
        calc.settings_toggle[calc.command_prefix + self.settings_toggle] = self.settings_name
        calc.settings_toggle[calc.command_prefix + self.settings_toggle2] = self.settings_name
        calc.register_plugin(self.helper)

    def parse_command(self, command: CalculatorCommand) -> None:
        """Executed at the start of command parsing"""
        self.profile.clear()
        if command.calc.settings[self.settings_name]:
            print("----------[ Output ]----------")
        self.profile.start_event("Command parsing", f"Parsing `{command.command_original}`")

    def handle_command(self, command: CalculatorCommand) -> None:
        """Executed at the start of command parsing"""
        self.profile.start_event("Command handling", f"Handling `{command.command}`")

    def handle_runtime_error(self, command: CalculatorCommand, data: str) -> None:
        self.profile.end_event()
        newline = "\n"
        self.profile.start_event("Runtime error handling", f"Handling `{data.split(newline)[-2]}`")

    def handle_syntax_error(self, command: CalculatorCommand, data: str) -> None:
        self.profile.end_event()
        newline = "\n"
        self.profile.start_event("Syntax error handling", f"Handling `{data.split(newline)[-2]}`")

    def handle_resend(self, command: CalculatorCommand) -> None:
        self.profile.end_event()
        self.profile.start_event("Resend parsing", f"Resend parsing `{command.command}`")

    def command_success(self, command: CalculatorCommand) -> None:
        self.profile.end_event()
        self.profile.start_event("Success handling", "Successfully executed command")

    def command_fail(self, command: CalculatorCommand) -> None:
        if self.profile.active_event is not None:
            if command.abort:
                self.profile.abort_event()
                self.profile.start_event("Failure handling", "Command aborted")
            else:
                self.profile.die_event()
                self.profile.start_event("Failure handling", "Command died")
        else:
            self.profile.start_event("Failure handling", "Command failed")
