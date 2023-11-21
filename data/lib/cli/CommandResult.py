#----------------------------------------------------------------------

    # Class
class CommandResult:
    def __init__(self, name: str, **kwargs: object) -> None:
        self._name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


    def exists(self, key: str) -> bool:
        return hasattr(self, key)


    def __str__(self) -> str:
        return f'{self._name}({", ".join([f"{key} = {value.__repr__()}" for key, value in self.__dict__.items() if key != "_name"])})'

    def __repr__(self) -> str:
        return self.__str__()
#----------------------------------------------------------------------
