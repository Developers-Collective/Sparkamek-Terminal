#----------------------------------------------------------------------

    # Libraries
from .MatchingFuncSymbol import MatchingFuncSymbol
#----------------------------------------------------------------------

    # Class
class CannotFindFunctionException(Exception):
    def __init__(self, not_found_func: str, func_symbols: list[MatchingFuncSymbol]) -> None:
        m = f'Cannot find function: {not_found_func}'
        super().__init__(m)

        self._msg = m
        self._not_found_func = not_found_func
        self._func_symbols = tuple(func_symbols)

    @property
    def msg(self) -> str:
        return self._msg

    @property
    def not_found_func(self) -> str:
        return self._not_found_func

    @property
    def func_symbols(self) -> tuple[MatchingFuncSymbol]:
        return self._func_symbols
#----------------------------------------------------------------------
