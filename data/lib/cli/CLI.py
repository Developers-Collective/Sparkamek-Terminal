#----------------------------------------------------------------------

    # Libraries
from .Choice import Choice
from .CLIException import CLIException
from .CommandResult import CommandResult
from .CLIConstants import CLIConstants
from .CommandMaxLengthStruct import CommandMaxLengthStruct
#----------------------------------------------------------------------

    # Class
class CLI:
    def __init__(self, executable: str, version: str, *choices: Choice) -> None:
        self._executable = executable
        self._version = version

        self._choices: dict[str, Choice] = {}
        for choice in choices:
            self._choices[choice.name] = choice


    @property
    def executable(self) -> str:
        return self._executable

    @property
    def version(self) -> str:
        return self._version

    @property
    def choices(self) -> dict[str, Choice]:
        return self._choices


    def add_choice(self, choice: Choice) -> None:
        self._choices[choice.name] = choice


    def get_choice(self, name: str) -> Choice | None:
        return self._choices.get(name, None)


    def _arg_parser(self, args: tuple[str]) -> tuple[str]:
        args_list = list(args)
        new_args_list = []

        while args_list:
            arg = args_list.pop(0)

            if (arg.startswith('\'') or arg.startswith('"')):
                if arg.endswith(arg[0]):
                    arg = arg[1:-1]

                else:
                    while args_list:
                        arg += ' ' + args_list.pop(0)
                        if arg.endswith(arg[0]):
                            break

                    if not arg.endswith(arg[0]): raise CLIException(f'Missing closing quote for argument {arg}', 0)
                    arg = arg[1:-1]

            new_args_list.append(arg)

        return tuple(new_args_list)


    def _exec_exceptions_handler(self, exceptions: dict[str, CLIException]) -> None:
        def single_exception_handler(exception: CLIException) -> None:
            print(f'{CLIConstants.ErrorLogColor.terminal_color}{exception}{CLIConstants.Reset}')

        if not exceptions:
            return print(f'{CLIConstants.ErrorLogColor.terminal_color}An error occured{CLIConstants.Reset}')

        max_steps = max([e.step for e in exceptions.values()])
        new_exceptions = dict(filter(lambda e: e[1].step >= max_steps, exceptions.items()))

        if new_exceptions:
            done_values = []
            for exception in new_exceptions.values():
                if exception.message in done_values: continue

                single_exception_handler(exception)
                done_values.append(exception.message)

            return

        for exception in exceptions.values():
            single_exception_handler(exception)


    def exec(self, *args: str) -> None:
        args_list = tuple(args)
        exceptions: dict[str, CLIException] = {}
        print()

        try: args_list = self._arg_parser(args_list)
        except CLIException as e: return print(f'{CLIConstants.ErrorLogColor.terminal_color}{e}{CLIConstants.Reset}')

        for choice in self._choices.values():
            try: return choice.exec(args_list)
            except CLIException as e: exceptions[choice.name] = e

        self._exec_exceptions_handler(exceptions)


    def display(self, help: CommandResult = None) -> None:
        max_length = CommandMaxLengthStruct.get_max(*(choice.get_display_length() for choice in self._choices.values()))
        max_length.apply_max_width()

        if not help.exists('command'):
            print(f'{CLIConstants.TitleColor.terminal_color}Usage{CLIConstants.Reset}')

            for choice in self._choices.values():
                choice.display_usage(self._executable)

            for choice in self._choices.values():
                choice.display(max_length)

            return

        command_name = help.command
        for choice in self._choices.values():
            for section_group in choice.section_groups:
                for section in section_group.sections:
                    if command := section.get_command(command_name):
                        command.display(max_length)
                        return

        print(f'{CLIConstants.ErrorLogColor.terminal_color}Unknown command {command_name}{CLIConstants.Reset}')
#----------------------------------------------------------------------
