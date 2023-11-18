#----------------------------------------------------------------------

    # Libraries
import os
from ..LogType import LogType
from .format_msg import format_msg
from .load_config import load_config
from .cmd import press_any_key, clear
from ..view import ChoiceWindow
#----------------------------------------------------------------------

    # Function
def compile_select():
    config, devkitppc_path = load_config()

    if not (devkitppc_path is not None and os.path.isdir(devkitppc_path)):
        print(format_msg('Unable to find devkitPPC path. Please set it manually in config.json', LogType.Error))
        press_any_key()
        return

    projects: list[dict] = config['projects']

    if len(projects) == 0:
        print(format_msg('No projects found in config.json', LogType.Error))
        press_any_key()
        return

    options = [f'{project["name"]}' for project in projects]

    selected_id = 0

    while True:
        app = ChoiceWindow(projects = options, selected_id = selected_id)
        selected_id = app.run()
        if selected_id is None: break
        clear()

        project = projects[selected_id]

        try: compile(project, devkitppc_path)
        except FileNotFoundError: break
#----------------------------------------------------------------------
