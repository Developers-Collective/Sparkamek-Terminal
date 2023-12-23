#----------------------------------------------------------------------

    # Setup
import os, sys
from data.lib.GlobalValues import GlobalValues
GlobalValues.old_path = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__ if sys.argv[0].endswith('.py') else sys.executable)))
#----------------------------------------------------------------------

    # Libraries
import json
from enum import StrEnum, Enum
from textual import *
from data.lib.CompilerWorker import CompilerWorker
from data.lib.LogType import LogType
from data.lib.view import *
from data.lib.cli import *
from data.lib.utils.Color import Color
from data.lib.PlatformType import PlatformType
from data.lib.version import VERSION_BUILD
from data.lib.path import *
from data.lib.main_functions import *
from data.lib.cliviews import *
from data.lib.cli_commands import *
#----------------------------------------------------------------------

    # Main
if __name__ == '__main__':
    if len(sys.argv) > 1:
        mainview(__file__ if sys.argv[0].endswith('.py') else sys.executable)

    else:
        clear()

        try: add_to_path()
        except Exception as e:
            print(format_msg(f'Unable to add to path: {e}', LogType.Error))
            press_any_key()

        compile_select()
#----------------------------------------------------------------------
