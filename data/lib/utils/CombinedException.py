#----------------------------------------------------------------------

    # Libraries
from typing import Sequence
import traceback
#----------------------------------------------------------------------

    # Class
class CombinedException(Exception):
    def __init__(self, exceptions: Sequence[Exception]) -> None:
        self._exceptions = tuple(exceptions)
        super().__init__('Combined exception occurred with multiple issues.')


    @property
    def exceptions(self) -> tuple[Exception]:
        return self._exceptions


    def __str__(self) -> str:
        combined_traceback = '\n'.join(
            f'Exception {i+1}: {traceback.format_exception(type(exc), exc, exc.__traceback__)}'
            for i, exc in enumerate(self.exceptions)
        )
        return f'{self.__class__.__name__} with tracebacks:\n{combined_traceback}'
#----------------------------------------------------------------------
