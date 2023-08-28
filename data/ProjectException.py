#----------------------------------------------------------------------

    # Libraries
from .LogType import LogType
#----------------------------------------------------------------------

    # Class
class ProjectException(Exception):
    def __init__(self, msg: str, type: LogType) -> None:
        super().__init__(msg)

        self._msg = msg
        self._type = type

    @property
    def msg(self) -> str:
        return self._msg

    @property
    def type(self) -> LogType:
        return self._type
#----------------------------------------------------------------------
