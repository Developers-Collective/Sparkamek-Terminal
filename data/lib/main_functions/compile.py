#----------------------------------------------------------------------

    # Libraries
import os
from ..LogType import LogType
from .format_msg import format_msg
from .cmd import press_any_key, clear
from ..GlobalValues import GlobalValues
from .logs import log_simple, log_complete
from ..CompilerWorker import CompilerWorker
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
