#----------------------------------------------------------------------

    # Libraries
from .CLIConstants import CLIConstants
from dataclasses import dataclass
import os
#----------------------------------------------------------------------

    # Struct
@dataclass
class CommandMaxLengthStruct:
    max_aliases: int
    max_arguments: int
    max_description: int


    @property
    def attributes_count(self) -> int:
        return self.__annotations__.keys().__len__()


    @property
    def total_length(self) -> int:
        return (
            self.max_aliases +
            self.max_arguments +
            CLIConstants.SpaceOffset +
            (CLIConstants.SpaceSeparator * self.attributes_count)
        )


    @staticmethod
    def get_max(*structs: 'CommandMaxLengthStruct') -> 'CommandMaxLengthStruct':
        max_aliases = max([struct.max_aliases for struct in structs])
        max_arguments = max([struct.max_arguments for struct in structs])
        max_description = 0 # Useless to calculate, will be calculated in apply_max_width

        return CommandMaxLengthStruct(max_aliases, max_arguments, max_description)


    def apply_max_width(self) -> None:
        length = self.total_length
        max_width = os.get_terminal_size().columns

        self.max_aliases += CLIConstants.SpaceSeparator
        self.max_arguments += CLIConstants.SpaceSeparator
        self.max_description = max(max_width - length, 0)
#----------------------------------------------------------------------
