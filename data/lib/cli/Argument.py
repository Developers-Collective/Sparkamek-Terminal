#----------------------------------------------------------------------

    # Libraries
from .ArgumentType import ArgumentType
#----------------------------------------------------------------------

    # Class
class Argument:
    def __init__(self, name: str, type: ArgumentType) -> None:
        self._name = name
        self._type = type


    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> ArgumentType:
        return self._type
#----------------------------------------------------------------------
