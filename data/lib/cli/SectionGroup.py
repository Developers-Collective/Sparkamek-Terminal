#----------------------------------------------------------------------

    # Libraries
from .CLIConstants import CLIConstants
from .Section import Section
from .CommandMaxLengthStruct import CommandMaxLengthStruct
#----------------------------------------------------------------------

    # Class
class SectionGroup:
    def __init__(self, name: str, *sections: Section) -> None:
        self._name = name
        self._sections: list[Section] = list(sections)


    @property
    def name(self) -> str:
        return self._name

    @property
    def sections(self) -> tuple[Section]:
        return tuple(self._sections)


    def add_section(self, section: Section) -> None:
        self._sections.append(section)


    def get_section(self, name: str) -> Section | None:
        for section in self._sections:
            if section.name == name:
                return section

        return None


    def exec(self, arg_list: tuple[str], input_step: int) -> tuple[dict[str, dict], tuple[str], int]:
        results = {}
        new_arg_list = list(arg_list)
        step = input_step
        
        for section in self._sections:
            result, new_arg_list, step = section.exec(new_arg_list, step + 1)
            results |= result

        return results, new_arg_list, step


    def get_display_length(self) -> CommandMaxLengthStruct:
        return CommandMaxLengthStruct.get_max(*(section.get_display_length() for section in self._sections))


    def display(self, max_length: CommandMaxLengthStruct) -> None:
        for section in self._sections:
            section.display(max_length)

    def display_usage(self, executable: str) -> None:
        print(' ' * CLIConstants.SpaceOffset, end = '')
        print(f'{CLIConstants.FontColor.terminal_color}"{executable}"{CLIConstants.Reset}', end = ' ')

        for section in self._sections:
            print(f'{section.type.value.replace("%s", section.name.replace("-", " ").title())}', end = ' ')

        print()
#----------------------------------------------------------------------
