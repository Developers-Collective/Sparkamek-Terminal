#----------------------------------------------------------------------

    # Libraries
from typing import Type, Callable
import types, inspect
#----------------------------------------------------------------------

    # Class
class Signal:
    def __init__(self, *types: Type) -> None:
        self._types = types
        self._funcs: list[Callable] = []

    def connect(self, func: Callable) -> None:
        if func in self._funcs: return
        self._funcs.append(func)

    def disconnect(self, func: Callable) -> None:
        self._funcs.remove(func)

    def disconnect_all(self) -> None:
        self._funcs = []

    def emit(self, *args) -> None:
        for arg, type_ in zip(args, self._types):
            if (isinstance(arg, types.GeneratorType) or inspect.isgenerator(arg)) and (type_ is list or type_ is tuple): continue
            assert isinstance(arg, type_), f'Expected {type_}, got {type(arg)}'

        for func in self._funcs:
            if isinstance(func, Signal): func.emit(*args)
            else: func(*args)
#----------------------------------------------------------------------
