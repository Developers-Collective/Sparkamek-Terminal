#----------------------------------------------------------------------

    # Libraries
import colorama
from .Choice import Choice
from .Section import Section
from .SectionGroup import SectionGroup
from .Command import Command
from .Argument import Argument
from .CLIConstants import CLIConstants
from .SectionType import SectionType
from .ArgumentType import ArgumentType
from .CLIException import CLIException
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


    def exec(self, *args: str) -> None:
        args_list = list(args)
        error = None
        leave = False
        kwargs = {}
        print()

        while args_list: # Not optimal but it works (idk why it works but it works lol)
            arg: str = args_list.pop(0)

            if not arg.startswith('-'):
                print()
                print(f'{colorama.Fore.LIGHTRED_EX}Unknown argument {arg}{colorama.Style.RESET_ALL}')
                continue

            for choice in self._choices.values():
                try:
                    for section_group in choice.section_groups:
                        for section in section_group.sections:
                            command = section.get_command(arg)

                            if command is None:
                                if section.type == SectionType.Mandatory:
                                    raise CLIException(f'Missing mandatory section {section.name}')
                                # raise CLIException(f'Unknown command {arg}')
                                continue
                            
                            arguments = {}
                            for argument in command.arguments:
                                if argument.type == ArgumentType.Mandatory:
                                    if not args_list:
                                        raise CLIException(f'Missing mandatory argument {argument.name} for command {command.name}')

                                if argument.type == ArgumentType.Optional:
                                    if not args_list:
                                        break

                                arg = args_list.pop(0)
                                if (arg.startswith('\'') or arg.startswith('"')):
                                    if arg.endswith(arg[0]):
                                        arg = arg[1:-1]

                                    else:
                                        while args_list:
                                            arg += ' ' + args_list.pop(0)
                                            if arg.endswith(arg[0]):
                                                break

                                        if not arg.endswith(arg[0]): return print(f'{colorama.Fore.LIGHTRED_EX}Missing closing quote for argument {argument.name}: {arg}{colorama.Style.RESET_ALL}')
                                        arg = arg[1:-1]

                                arguments[argument.name] = arg
                                continue

                            if kwargs.get(section.name.replace('-', '_'), None) is None: kwargs[section.name.replace('-', '_')] = {}
                            kwargs[section.name.replace('-', '_')][command.name.replace('-', '_')] = arguments.copy()


                    if args_list:
                        leave = True
                        raise CLIException(f'Unknown argument {args_list[0]}')

                    choice.exec(**kwargs)
                    return

                except CLIException as e:
                    error = e
                    if not leave: continue
                    else: break

            if leave: break

        if not error:
            print(f'{colorama.Fore.LIGHTRED_EX}An error occured{colorama.Style.RESET_ALL}')
            return

        print(f'{colorama.Fore.LIGHTRED_EX}{error}{colorama.Style.RESET_ALL}')


    def display(self, help: str = None) -> None:
        if not help.get('help', None):
            print(f'{colorama.Fore.LIGHTBLUE_EX}Usage{colorama.Style.RESET_ALL}')

            for choice in self._choices.values():
                choice.display_usage(self._executable)

            for choice in self._choices.values():
                choice.display()

            return

        command_name = help['help']['command']
        for choice in self._choices.values():
            for section_group in choice.section_groups:
                for section in section_group.sections:
                    if command := section.get_command(command_name):
                        command.display()
                        return

        print(f'{colorama.Fore.LIGHTRED_EX}Unknown command {command_name}{colorama.Style.RESET_ALL}')
#----------------------------------------------------------------------
