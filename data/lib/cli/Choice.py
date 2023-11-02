#----------------------------------------------------------------------

    # Libraries
import colorama
from typing import Callable

from .SectionGroup import SectionGroup
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


    def display(self) -> None:
        for section_group in self._section_groups.values():
            section_group.display()

    def display_usage(self, executable: str) -> None:
        for section_group in self._section_groups.values():
            section_group.display_usage(executable)


    def exec(self, *args, **kwargs) -> None:
        if self._callback is not None: self._callback(*args, **kwargs)
#----------------------------------------------------------------------
