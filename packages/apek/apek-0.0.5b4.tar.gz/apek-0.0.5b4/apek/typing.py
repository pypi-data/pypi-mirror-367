# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring


import time as _time


class BuiltIn():
    NoneType = type(None)
    NotImplementedType = type(NotImplemented)
    builtin_function_or_method = type(print)
    function = type(lambda: None)


class _DataTransmitor():
    def __init__(self, instance):
        self.name = type(instance).__name__
        self.data = instance.as_group(list)
        self.mdata = instance.as_dict()


class BaseObject():
    def __init__(self):
        self._createdTime = str(round(_time.time(), 4))
        self._classNameOfSelf = f"{__name__}.{type(self).__name__}"
    
    def __repr__(self):
        return f"<class {self._classNameOfSelf} created at {self._createdTime}>"
    
    def __bool__(self):
        return True


class Number(BaseObject):
    pass


class Null(BaseObject):
    def __repr__(self):
        return f"<class {self._classNameOfSelf}>"
    
    def __bool__(self):
        return False
