#----------------------------------------------------------------------

    # Libraries
import math
from typing import Callable

from .SectionGroup import SectionGroup
from .CLIException import CLIException
from .CommandMaxLengthStruct import CommandMaxLengthStruct
#----------------------------------------------------------------------

    # Class
class Choice:
    def __init__(self, name: str, callback: Callable, *section_groups: SectionGroup) -> None:
        self._name = name
        self._callback = callback
        self._section_groups: dict[str, SectionGroup] = {}

        for section_group in section_groups:
            self._section_groups[section_group.name] = section_group


    @property
    def name(self) -> str:
        return self._name

    @property
    def callback(self) -> Callable:
        return self._callback

    @property
    def section_groups(self) -> list[SectionGroup]:
        return list(self._section_groups.values())


    def add_section_group(self, section_group: SectionGroup) -> None:
        self._section_groups[section_group.name] = section_group


    def get_display_length(self) -> CommandMaxLengthStruct:
        return CommandMaxLengthStruct.get_max(*(section_group.get_display_length() for section_group in self._section_groups.values()))

    def display(self, max_length: CommandMaxLengthStruct) -> None:
        for section_group in self._section_groups.values():
            section_group.display(max_length)

    def display_usage(self, executable: str) -> None:
        for section_group in self._section_groups.values():
            section_group.display_usage(executable)


    def call(self, *args, **kwargs) -> bool:
        if self._callback is not None: self._callback(*args, **kwargs)


    def exec(self, arg_list: tuple[str]) -> None:
        results = {}

        for section_group in self._section_groups.values():
            result, new_arg_list, _ = section_group.exec(arg_list, 1)
            results |= result

        if new_arg_list:
            raise CLIException(f'Unknown extra argument: {new_arg_list[0]}', math.inf)

        return self.call(**results)
#----------------------------------------------------------------------
