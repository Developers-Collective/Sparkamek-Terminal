#----------------------------------------------------------------------

    # Libraries
import colorama

from .SectionType import SectionType
from .Command import Command
#----------------------------------------------------------------------

    # Class
class Section:
    def __init__(self, name: str, type: SectionType, *commands: Command) -> None:
        self._name = name
        self._type = type

        self._commands: dict[str, Command] = {}
        for command in commands:
            self._commands[command.name] = command


    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> SectionType:
        return self._type

    @property
    def commands(self) -> dict[str, Command]:
        return self._commands


    def add_command(self, command: Command) -> None:
        self._commands[command.name] = command


    def get_command_by_name(self, name: str) -> Command | None:
        return self._commands.get(name, None)


    def get_command(self, key: str) -> Command | None:
        for command in self._commands.values():
            if key in command.aliases:
                return command

        return None


    def display(self) -> None:
        self.display_name()

        for command in sorted(self._commands.values(), key = lambda c: c.name):
            command.display()


    def display_name(self) -> None:
        print()
        print(f'{colorama.Fore.LIGHTBLUE_EX}{self._name}{colorama.Style.RESET_ALL}')
#----------------------------------------------------------------------
