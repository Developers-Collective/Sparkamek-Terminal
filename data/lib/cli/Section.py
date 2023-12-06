#----------------------------------------------------------------------

    # Libraries
from .SectionType import SectionType
from .Command import Command
from .CLIConstants import CLIConstants
from .CLIException import CLIException
from .CommandMaxLengthStruct import CommandMaxLengthStruct
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


    def exec(self, arg_list: tuple[str], input_step: int) -> tuple[dict[str, dict], tuple[str], int]:
        results = {}
        new_arg_list = list(arg_list)
        step = input_step

        for command in self._commands.values():
            try:
                result, new_arg_list, step = command.exec(new_arg_list, step + 1)
                results |= result

            except CLIException as e:
                if self.type == SectionType.Mandatory:
                    raise e
                continue

        return results, new_arg_list, step


    def get_display_length(self) -> CommandMaxLengthStruct:
        return CommandMaxLengthStruct.get_max(*(command.get_display_length() for command in self._commands.values()))


    def display(self, max_length: CommandMaxLengthStruct) -> None:
        self.display_name()

        for command in sorted(self._commands.values(), key = lambda c: c.name):
            command.display(max_length)


    def display_name(self) -> None:
        print()
        print(f'{CLIConstants.TitleColor.terminal_color}{self._name.replace("-", " ").title()}{CLIConstants.Reset}')
#----------------------------------------------------------------------
