#----------------------------------------------------------------------

    # Class
class CLIException(Exception):
    def __init__(self, message: str, step: int) -> None:
        super().__init__()
        self._message = message
        self._step = step

    @property
    def message(self) -> str:
        return self._message

    @property
    def step(self) -> int:
        return self._step

    def __str__(self) -> str:
        return self._message
#----------------------------------------------------------------------
