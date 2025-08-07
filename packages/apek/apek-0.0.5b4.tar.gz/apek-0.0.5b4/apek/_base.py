# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring


def _checkAndShowArgumentTypeError(varName, var, varType):
    if isinstance(var, varType):
        return
    s = None
    if isinstance(varType, type):
        s = varType.__name__
    elif isinstance(varType, (tuple, list)):
        if len(varType) == 1:
            s = varType[0].__name__
        elif len(varType) == 2:
            s = varType[0].__name__ + " or " + varType[1].__name__
        elif len(varType) >= 3:
            bl = varType[:-1]
            s = ", ".join([i.__name__ for i in bl]) + " or " + varType[-1].__name__
    raise TypeError(f"The argument \"{varName}\" must be {s}, but gived {type(var).__name__}.")


def _checkAndthrowInvalidValue(varName, var, validValues):
    if var not in validValues:
        raise ValueError(f"The argument \"{varName}\" cannot be {repr(var)}, only be one of them: {tuple(map(lambda x: x.__name__ if isinstance(x, type) else x, validValues))}")


def _typeRepr(value):
    return f"<instance of {value.__name__}>"
