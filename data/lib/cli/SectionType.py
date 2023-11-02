#----------------------------------------------------------------------

    # Libraries
from enum import StrEnum
import colorama
#----------------------------------------------------------------------

    # Class
class SectionType(StrEnum):
    Mandatory = f'{colorama.Fore.LIGHTGREEN_EX}<%s>{colorama.Style.RESET_ALL}'
    Optional = f'{colorama.Fore.LIGHTCYAN_EX}[%s]{colorama.Style.RESET_ALL}'
#----------------------------------------------------------------------
