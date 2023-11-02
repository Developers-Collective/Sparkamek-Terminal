#----------------------------------------------------------------------

    # Libraries
import colorama
from typing import Callable

from .Argument import Argument
from .ArgumentType import ArgumentType
from .CLIConstants import CLIConstants
#----------------------------------------------------------------------

    # Class
class Command:
    def __init__(self, name: str, description: str, aliases: list[str] | tuple[str], arguments: list[Argument] | tuple[Argument] = []) -> None:
        self._name = name
        self._aliases = tuple(aliases)
        self._description = description
        self._arguments = tuple(arguments)

        found_optional = False
        for argument in self._arguments:
            if argument.type == ArgumentType.Mandatory and found_optional: raise ValueError('Mandatory arguments must be at the beginning of the arguments list')
            if argument.type == ArgumentType.Optional: found_optional = True


    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def aliases(self) -> tuple[str]:
        return self._aliases

    @property
    def arguments(self) -> tuple[Argument]:
        return self._arguments


    def display(self) -> None:
        aliases = ', '.join(self._aliases)
        len_aliases = len(aliases)

        arguments = ' '.join([argument.type.value.replace('%s', argument.name) for argument in self._arguments])
        len_arguments = len(' '.join([f'[{argument.name}]' for argument in self._arguments]))

        desc = self._description.split('\n')

        print(' ' * CLIConstants.SPACE_ALIGN, end = '')
        print(f'{colorama.Fore.LIGHTYELLOW_EX}{aliases}{colorama.Style.RESET_ALL}', end = '')
        print(' ' * (CLIConstants.SPACE_ARGS_ALIGN - len_aliases), end = '')
        print(f'{arguments}', end = '')
        print(' ' * (CLIConstants.SPACE_COMMENT_ALIGN - len_arguments), end = '')
        print(f'{colorama.Fore.LIGHTWHITE_EX}{desc[0]}{colorama.Style.RESET_ALL}')

        for line in desc[1:]:
            print(' ' * (CLIConstants.SPACE_COMMENT_ALIGN + CLIConstants.SPACE_ARGS_ALIGN + CLIConstants.SPACE_ALIGN), end = '')
            print(f'{colorama.Fore.LIGHTWHITE_EX}{line}{colorama.Style.RESET_ALL}')
#----------------------------------------------------------------------
