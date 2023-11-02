#----------------------------------------------------------------------

    # Libraries
import colorama

from .CLIConstants import CLIConstants
from .Section import Section
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


    def display(self) -> None:
        for section in self._sections:
            section.display()

    def display_usage(self, executable: str) -> None:
        print(' ' * CLIConstants.SPACE_ALIGN, end = '')
        print(f'{colorama.Fore.LIGHTWHITE_EX}"{executable}"{colorama.Style.RESET_ALL}', end = ' ')

        for section in self._sections:
            print(f'{section.type.value.replace("%s", section.name)}', end = ' ')

        print()
#----------------------------------------------------------------------
