#----------------------------------------------------------------------

    # Libraries
from .Argument import Argument
from .ArgumentType import ArgumentType
from .CLIConstants import CLIConstants
from .CLIException import CLIException
from .CommandResult import CommandResult
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


    def _fix_name(self, name: str) -> str:
        authorized = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
        new_name = ''.join([char if char in authorized else '_' for char in name])
        if new_name[0] in '0123456789': new_name = '_' + new_name

        return new_name


    def exec(self, arg_list: tuple[str], input_step: int) -> tuple[dict[str, str], tuple[str], int]:
        results = {}
        new_arg_list = list(arg_list)
        step = input_step

        if not new_arg_list[0] in self._aliases:
            raise CLIException(f'Unknown command: {new_arg_list[0]}', step)
        
        new_arg_list.pop(0)
        fixed_name = self._fix_name(self._name)
        results[fixed_name] = CommandResult(self._name)
        command_args = {}

        for argument in self._arguments:
            step += 1
            if not new_arg_list:
                if argument.type == ArgumentType.Optional: continue
                else: raise CLIException(f'Missing argument: {argument.name}', step)

            arg = new_arg_list.pop(0)
            command_args[argument.name] = arg

        if command_args:
            results[fixed_name] = CommandResult(self._name, **command_args)

        return results, tuple(new_arg_list), step


    def display(self) -> None:
        aliases = ', '.join(self._aliases)
        len_aliases = len(aliases)

        arguments = ' '.join([argument.type.value.replace('%s', argument.name) for argument in self._arguments])
        len_arguments = len(' '.join([f'[{argument.name}]' for argument in self._arguments]))

        desc = self._description.split('\n')

        print(' ' * CLIConstants.SpaceAlign, end = '')
        print(f'{CLIConstants.YellowColor.terminal_color}{aliases}{CLIConstants.Reset}', end = '')
        print(' ' * (CLIConstants.SpaceArgsAlign - len_aliases), end = '')
        print(f'{arguments}', end = '')
        print(' ' * (CLIConstants.SpaceCommentAlign - len_arguments), end = '')
        print(f'{CLIConstants.WhiteColor.terminal_color}{desc[0]}{CLIConstants.Reset}')

        for line in desc[1:]:
            print(' ' * (CLIConstants.SpaceCommentAlign + CLIConstants.SpaceArgsAlign + CLIConstants.SpaceAlign), end = '')
            print(f'{CLIConstants.WhiteColor.terminal_color}{line}{CLIConstants.Reset}')
#----------------------------------------------------------------------
