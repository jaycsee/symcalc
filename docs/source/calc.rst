.. currentmodule:: symcalc

Calculator
==========

The :class:`Calculator` class contains the framework for user plugin interactions using data classes :class:`CalculatorContext` and :class:`CalculatorCommand`

.. autoclass:: Calculator
    :members:
    :exclude-members: notify_plugins_parse,
        notify_plugins_command,
        notify_plugins_resend,
        notify_plugins_syntax_error,
        notify_plugins_runtime_error,
        notify_plugins_success,
        notify_plugins_fail
    :member-order: bysource

    .. method:: notify_plugins_parse(command_data)
        notify_plugins_command(command_data)
        notify_plugins_resend(command_data)
        notify_plugins_syntax_error(command_data)
        notify_plugins_runtime_error(command_data)
        notify_plugins_success(command_data)
        notify_plugins_fail(command_data)

        Notify all plugins of a command to be parsed. The given ``command_data`` can be modified in place to direct the calculator to perform subsequent actions. See :class:`CalculatorCommand`

        :param command_data: The command which triggered this event
        :type command_data: :class:`CalculatorCommand`

.. autoclass:: CalculatorContext
    :members:
    :member-order: bysource

.. autoclass:: CalculatorCommand
    :members:
    :member-order: bysource

    .. py:attribute:: abort
        resend_command
        print_error
        success

        Directives to tell the :class:`Calculator` what to do after the plugin returns. Setting ``abort`` and ``resend_command`` prevents further plugin processing of the command