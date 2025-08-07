# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=duplicate-code


import copy as _cp
from mpmath import mp as _mp
from . import typing
from ._base import _checkAndShowArgumentTypeError


class LargeNumber(typing.Number):
    """
    Handle large numbers through the class.
    
    Attributes:
        base (float): The base part of the number.
        exp (int): The exponent part of the number.
        cfg (dict): The dictionary that stores dispPrec, realPrec, reprUnits_en, and reprUnits_zh.
    
    Methods:
        parseString:
            Convert the LargeNumber instance to a string formatting.
        parseInt:
            Convert the LargeNumber instance to a integer.
        parseFloat:
            Convert the LargeNumber instance to a floating number.
        getBase:
            Get the base of the LargeNumber instance.
        getExp:
            Get the exponent of the LargeNumber instance.
        getConfig:
            Get the specified configuration item or all configuration information.
    """
    
    def _tryParseLargeNumberOrReturnNone(self, n):
        try:
            if isinstance(n, (int, float)):
                with _mp.workdps(self.getConfig("realPrec")):
                    n = _mp.mpf(n)
            if isinstance(n, _mp.mpf):
                temp = object.__new__(self.__class__)
                temp.config = self.getConfig()
                temp.exp = 0
                temp.base = n
                temp.calibrate()
                return temp
        except (TypeError, ValueError, OverflowError):
            return None
        if isinstance(n, self.__class__):
            return n
        return None
    
    def __init__(
        self,
        base = 0,
        exp = 0,
        *,
        dispPrec = 4,
        realPrec = 8,
        reprUnits_en = "KMBTPEZY",
        reprUnits_zh = "万亿兆京垓秭穰"
    ):
        """
        Provide parameters "base" and "exp" to create an instance of LargeNumber.
        
        The specific value of LargeNumber is set through "base" and "exp",
        and it also supports setting precision and display unit table.
        
        Args:
            base (int or float or LargeNumber, optional):
                "base" is used to control the base part of LargeNumber, that is the "X" in "XeY",
                and its range will be automatically calibrated to [1, 10).
                The corresponding "exp" will be modified.
                The default is 0.
            exp (int or LargeNumber, optional):
                "exp" is used to control the exponent part of LargeNumber, that is the "Y" in "XeY".
                The default is 0.
            dispPrec (int, optional):
                Keyword argument.
                Controls the decimal precision when displaying.
                Parts below the precision will be automatically rounded.
                It cannot be greater than "realPrec" and cannot be negative.
                The default is 4.
            realPrec (int, optional):
                Keyword argument.
                Controls the decimal precision during actual calculations.
                Parts below the precision will be discarded.
                It cannot be less than "dispPrec" and cannot be negative.
                The default is 8.
            reprUnits_en (str or list or tuple, optional):
                Keyword argument.
                Controls the English units used for the exponent part when converting a LargeNumber instance with a large "exp" to a string.
                When accepting a str, each character is treated as a unit.
                When accepting a list or tuple, each item is treated as a unit.
                The units are ordered from smallest to largest from the beginning to the end.
                The iterable object must not be empty.
            reprUnits_zh (str or list or tuple, optional):
                Keyword argument.
                Controls the Chinese units used for the exponent part when converting a LargeNumber instance with a large "exp" to a string.
                When accepting a str, each character is treated as a unit.
                When accepting a list or tuple, each item is treated as a unit.
                The units are ordered from smallest to largest from the beginning to the end. The iterable object must not be empty.
        
        Returns:
            None
        
        Raises:
            TypeError: A TypeError will be thrown when the number or type of the accepted arguments is incorrect.
            ValueError: A ValueError will be thrown when the value of the accepted arguments is incorrect.
        """
        
        _checkAndShowArgumentTypeError("base", base, (int, float, str, _mp.mpf))
        _checkAndShowArgumentTypeError("exp", exp, (int, str, _mp.mpf))
        if isinstance(exp, _mp.mpf):
            exp = int(exp)
        super().__init__()
        cfg = {}
        _checkAndShowArgumentTypeError("dispPrec", dispPrec, int)
        if dispPrec < 0:
            raise ValueError("The parameter 'dispPrec' cannot be less than 0.")
        cfg["dispPrec"] = dispPrec
        _checkAndShowArgumentTypeError("realPrec", realPrec, int)
        if realPrec < 0:
            raise ValueError("The parameter 'realPrec' cannot be less than 0.")
        if realPrec > 999999:
            raise ValueError("The parameter 'realPrec' is too large.")
        if realPrec < dispPrec:
            raise ValueError("The parameter 'realPrec' cannot be less than parameter 'dispPrec'.")
        cfg["realPrec"] = realPrec
        _checkAndShowArgumentTypeError("reprUnits_en", reprUnits_en, (list, tuple, str))
        if not reprUnits_en:
            raise ValueError(f"The paramter 'reprUnits_en' cannot be empty {type(reprUnits_en).__name__}.")
        cfg["reprUnits_en"] = reprUnits_en
        _checkAndShowArgumentTypeError("reprUnits_zh", reprUnits_zh, (list, tuple, str))
        if not reprUnits_zh:
            raise ValueError(f"The paramter 'reprUnits_zh' cannot be empty {type(reprUnits_zh).__name__}.")
        cfg["reprUnits_zh"] = reprUnits_zh
        self.config = cfg
        
        
        base = self._toMpf(base)
        self.sign = 1 if base >= 0 else -1
        self.base = abs(base)
        self.exp = exp
        self.calibrate()
    
    def getBase(self):
        return self.base * self.getSign()
    
    def setBase(self, value, *, _noCalibrate=False):
        _checkAndShowArgumentTypeError("value", value, (int, float, str, _mp.mpf))
        self.setSign(1 if value >= 0 else -1)
        if not isinstance(value, _mp.mpf):
            self.base = abs(_mp.mpf(value))
        else:
            self.base = abs(value)
        if self.base == 0:
            self.setExp(0)
        if _noCalibrate:
            return
        self.calibrate()
    
    def getExp(self):
        return int(self.exp)
    
    def setExp(self, exp):
        _checkAndShowArgumentTypeError("exp", exp, int)
        self.exp = exp
    
    def getSign(self):
        try:
            return self.sign
        except AttributeError:
            self.sign = 1
            return 1
        # Todo: 修复找不到sign的AttributeError
    
    def setSign(self, sign):
        _checkAndShowArgumentTypeError("sign", sign, int)
        if sign not in (1, -1):
            raise ValueError(f"The sign cannot be {sign}.")
        self.sign = sign
    
    def getConfig(self, key=None):
        if key is None:
            return _cp.deepcopy(self.config)
        _checkAndShowArgumentTypeError("key", key, str)
        if key not in self.config:
            raise KeyError(f"Key {key} not found in the config.")
        return self.config.get(key)
    
    def setConfig(self, key, value):
        _checkAndShowArgumentTypeError("key", key, str)
        if key in ["dispPrec", "realPrec"]:
            _checkAndShowArgumentTypeError("value", value, int)
            self.config[key] = value
        elif key in ["reprUnits_en", "reprUnits_zh"]:
            _checkAndShowArgumentTypeError("value", value, (str, list, tuple))
            self.config[key] = value
        else:
            raise KeyError(f"Key {key} not found in the config.")
    
    def _toMpf(self, base):
        if isinstance(base, _mp.mpf):
            return base
        with _mp.workdps(self.getConfig("realPrec")):
            return _mp.mpf(str(base))
    
    def calibrate(self):
        "Calibrate the instance."
        
        base, exp = self.base, self.exp
        
        if base == 0:
            self.base = _mp.mpf(0)
            self.exp = 0
            return
        
        expOfBase = int(_mp.floor(_mp.log10(base)))
        exp = exp + expOfBase
        calibratedBase = base / _mp.power(10, expOfBase)
        
        scale = _mp.power(10, self.getConfig("realPrec") - 1)
        calibratedBase = _mp.floor(calibratedBase * scale) / scale
        
        if calibratedBase >= 10:
            calibratedBase /= 10
            exp += 1
        
        if not isinstance(calibratedBase, _mp.mpf):
            with _mp.workdps(self.getConfig("realPrec")):
                self.base = calibratedBase
        else:
            self.base = calibratedBase
        self.exp = int(exp)
    
    def _insertUnit(self, number, mul, units):
        if number < mul:
            return str(number)
        for unit in units:
            number = round(number / mul, self.getConfig("realPrec"))
            if number < mul:
                return f"{number}{unit}"
        return f"{number}{units[-1]}"
    
    def copy(self):
        "Copy the instance as a new instance."
        
        new = object.__new__(self.__class__)
        new.base = self.base
        new.exp = self.exp
        new.sign = self.sign
        new.config = self.getConfig()
        return new
    
    __copy__ = copy
    
    def fastNew(self, base, exp, *, _fastly=False):
        "Fastly create an instance."
        
        new = object.__new__(self.__class__)
        new.base = base
        new.exp = exp
        new.config = self.getConfig()
        if _fastly is False:
            new.calibrate()
        return new
    
    def parseString(self, *, prec="default", expReprMode="none", template="{base}e{exp}", alwaysUseTemplate=False):
        """
        Convert LargeNumber to a string
        
        Args:
            prec (int or "default"):
                Keyword argument.
                The precision of the converted string.
                Defaults to the value of dispPrec.
            expReprMode ("none" or "comma" or "byUnit_en" or "byUnit_zh" or "power"):
                Keyword argument.
                Controls the display mode of the exponent.
                Defaults to "none".
            template (str):
                Keyword argument.
                Controls the template for inserting the base and exponent when converting to a string.
                Defaults to "{base}e{exp}".
            alwaysUseTemplate (bool):
                Keyword argument.
                Controls whether to always use the template.
                Defaults to False.
        
        Returns:
            str: The converted string.
        
        Raises:
            TypeError:
                This error is raised when the number or position of the arguments is incorrect,
                or the argument type is wrong.
        """
        self.calibrate()
        
        if prec == "default":
            prec = self.getConfig("dispPrec")
        elif prec == "real":
            prec = self.getConfig("realPrec")
        _checkAndShowArgumentTypeError("prec", prec, int)
        _checkAndShowArgumentTypeError("expReprMode", expReprMode, str)
        _checkAndShowArgumentTypeError("alwaysUseTemplate", alwaysUseTemplate, bool)
        base, exp = self.getBase(), self.getExp()
        if -4 <= exp <= 7 and not alwaysUseTemplate:
            return str(base * _mp.power(10, exp))
        dispBase = str(round(base * _mp.power(10, prec)) / _mp.power(10, prec))
        dispExp = None
        if exp >= 1_000_000_000_000_000 or exp <= -10:
            expReprMode = "power"
        if expReprMode == "comma":
            dispExp = f"{exp:,}"
        elif expReprMode == "none":
            dispExp = str(exp)
        elif expReprMode == "byUnit_en":
            dispExp = self._insertUnit(exp, 1000, self.getConfig("reprUnits_en"))
        elif expReprMode == "byUnit_zh":
            dispExp = self._insertUnit(exp, 10000, self.getConfig("reprUnits_zh"))
        elif expReprMode == "power":
            dispExp = str(LargeNumber(exp, 0))
        else:
            raise ValueError(f"Invalid expReprMode: {repr(expReprMode)}")
        return template.format(base=dispBase, exp=dispExp)
    
    def parseInt(self):
        """
        Convert the string to an integer.
        
        Returns:
            int:
                The converted integer.
        """
        return int(self.getBase() * _mp.power(10, self.getExp()))
    
    def __str__(self):
        return self.parseString()
    
    def __bool__(self):
        if self.getBase() == 0 and self.getExp() == 0:
            return False
        return True
    
    def __int__(self):
        return self.parseInt()
    
    def __float__(self):
        return float(self.parseString(prec="real"))
    
    def __repr__(self):
        return f"{self.getBase()}e{int(self.getExp()):,}"
    
    def __iter__(self):
        yield self.getBase()
        yield self.getExp()
        yield self.getConfig()
    
    def __neg__(self):
        return LargeNumber(-self.getBase(), self.getExp())
    
    def __pos__(self):
        return self
    
    def __abs__(self):
        return LargeNumber(abs(self.getBase()), self.getExp())
    
    def __eq__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if other is not None:
            return (self.getBase() == other.getBase()) and (self.getExp() == other.exp)
        return NotImplemented
    
    def __ne__(self, other):
        return not self == other
    
    def __lt__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if other is None:
            return NotImplemented
        if (ss := self.getSign()) != (os := other.getSign()):
            return ss < os
        if (se := self.getExp()) != (oe := other.getExp()):
            r = se < oe
            return r if self.getSign() == 1 else not r
        return self.getBase() < other.getBase()
    
    def __le__(self, other):
        return self < other or self == other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other
    
    def _addLargeNumbersAndReturnTuple(self, a, b):
        with _mp.workdps(a.getConfig("realPrec")):
            ra = a.getBase() * _mp.power(10, a.getExp())
            rb = b.getBase() * _mp.power(10, b.getExp())
            r = ra + rb
            s = 1 if r >= 0 else -1
            b, e = mpfToTuple(r._mpf_, 10)[1:]
            d = 0
            for i in b:
                d = d * 10 + 1
            b = d
            return b * s, e
            
    
    def __add__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if rv is None:
            return NotImplemented
        base, exp = self._add(copy.deepcopy(self), rv)
        return self.fastNew(base, exp)
    
    def __radd__(self, other):
        return self + other
    
    def __iadd__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if rv is None:
            return NotImplemented
        base, exp = self._add(copy.deepcopy(self), rv)
        self.setBase(base, _noCalibrate=True)
        self.setExp(exp)
        self.calibrate()
        return self
    
    def __sub__(self, other):
        return -other + self
    
    def __rsub__(self, other):
        return -self + other
    
    def __isub__(self, other):
        return self - other
    
    def __mul__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if rv is None:
            return NotImplemented
        if rv.getBase() == 0:
            return self.fastNew(0, 0, _fastly=True)
        return self.fastNew(
            self.getBase() * rv.getBase(),
            self.getExp() + rv.getExp()
        )
    
    def __rmul__(self, other):
        return self * other
    
    def __imul__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if rv is None:
            return NotImplemented
        if rv.getBase() == 0:
            self.setBase(0)
            self.setExp(0)
            return self
        self.setBase(self.getBase() * rv.getBase())
        self.setExp(self.getExp() + rv.getExp())
        return self
    
    def __truediv__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if rv is None:
            return NotImplemented
        if rv.getBase() == 0:
            raise ZeroDivisionError(f"{self.__class__.__name__} cannot division by 0.")
        return self.fastNew(
            self.getBase() / rv.getBase(),
            self.getExp() - rv.getExp()
        )
    
    def __rtruediv__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if rv is None:
            return NotImplemented
        return rv / self
    
    def __itruediv__(self, other):
        rv = self._tryParseLargeNumberOrReturnNone(other)
        if rv is None:
            return NotImplemented
        if rv.getBase() == 0:
            raise ZeroDivisionError(f"{self.__class__.__name__} cannot division by 0.")
        self.setBase(self.getBase() / rv.getBase())
        self.setExp(self.getExp() - rv.getExp())
        return self
    
    def asTuple(self):
        return (
            self.getBase(),
            self.getExp(),
            self.getConfig()
        )
    
    def asDict(self):
        return {
            "base": self.getBase(),
            "exp": self.getExp(),
            "config": self.getConfig()
        }
    
    def parseMpf(self, prec):
        _checkAndShowArgumentTypeError("prec", prec, int)
        with _mp.workdps(prec):
            return _mp.mpf(self.parseString(prec="real"))
