#----------------------------------------------------------------------

    # Libraries
import os
from ...LogType import LogType
from ...GlobalValues import GlobalValues
from ...CompilerWorker import CompilerWorker
from ...main_functions.format_msg import format_msg
from ...main_functions.cmd import press_any_key, clear
from ...main_functions.logs import log_simple, log_complete
#----------------------------------------------------------------------

    # Function
def compile(project: dict, devkitppc_path: str) -> None:
    GlobalValues.simple_logs = project['simpleLogs']

    if not os.path.exists(project['path']):
        print(format_msg(f'Unable to find path for project {project["name"]}', LogType.Error))
        press_any_key()
        clear()
        raise FileNotFoundError()

    clear()

    worker = CompilerWorker(
        data = project,
        devkitppc_path = devkitppc_path
    )
    worker.log_simple.connect(log_simple)
    worker.log_complete.connect(log_complete)
    worker.run()

    press_any_key()
    clear()
#----------------------------------------------------------------------
