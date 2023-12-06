#----------------------------------------------------------------------

    # Libraries
from .Argument import Argument
from .ArgumentType import ArgumentType
from .CLIConstants import CLIConstants
from .CLIException import CLIException
from .CommandResult import CommandResult
from .CommandMaxLengthStruct import CommandMaxLengthStruct
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


    def get_display_length(self) -> CommandMaxLengthStruct:
        aliases = ', '.join(self._aliases)
        arguments = ' '.join([f'[{argument.name}]' for argument in self._arguments])

        return CommandMaxLengthStruct(
            max_aliases = len(aliases),
            max_arguments = len(arguments),
            max_description = 0
        )


    def _print_align(self, string: str, len_string: int, max_length: int) -> None:
        print(string, end = '')
        print(' ' * (max_length - len_string), end = '')


    def display(self, max_length: CommandMaxLengthStruct) -> None:
        aliases = ', '.join(self._aliases)
        arguments = ' '.join([argument.type.value.replace('%s', argument.name) for argument in self._arguments])
        len_arguments = len(' '.join([f'[{argument.name}]' for argument in self._arguments]))
        desc = self._description.replace('\n', ' ').replace('\t', ' ').strip()

        self._print_align(
            f'{CLIConstants.CommandColor.terminal_color}{aliases}{CLIConstants.Reset}',
            len(aliases),
            max_length.max_aliases
        )
        self._print_align(
            f'{CLIConstants.FontColor.terminal_color}{arguments}{CLIConstants.Reset}',
            len_arguments,
            max_length.max_arguments
        )

        desc_lines: list[str] = []
        line_words: list[str] = []
        word: str = ''

        while desc:
            c = desc[0]
            desc = desc[1:]

            if c == ' ':
                if not word: continue

                line = ' '.join(line_words)

                if len(line) + len(word) + 1 > max_length.max_description:
                    desc_lines.append(line)
                    line_words = []

                line_words.append(word)
                word = ''

            else:
                word += c

        if word: line_words.append(word)

        if line_words: desc_lines.append(' '.join(line_words))

        l1 = desc_lines.pop(0)
        if max_length.max_description == 0: print()
        print(f'{CLIConstants.FontColor.terminal_color}{l1}{CLIConstants.Reset}')

        for line in desc_lines:
            if max_length.max_description != 0:
                print(
                    ' ' * (
                        max_length.total_length - (CLIConstants.SpaceSeparator * max_length.attributes_count) - CLIConstants.SpaceOffset
                    ),
                    end = ''
                )
            print(f'{CLIConstants.FontColor.terminal_color}{line}{CLIConstants.Reset}')
#----------------------------------------------------------------------
