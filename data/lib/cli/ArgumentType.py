#----------------------------------------------------------------------

    # Libraries
from enum import StrEnum
from .CLIConstants import CLIConstants
#----------------------------------------------------------------------

    # Class
class ArgumentType(StrEnum):
    Mandatory = CLIConstants.MandatoryColor.terminal_color + '<%s>' + CLIConstants.Reset
    Optional = CLIConstants.OptionalColor.terminal_color + '[%s]' + CLIConstants.Reset
#----------------------------------------------------------------------
