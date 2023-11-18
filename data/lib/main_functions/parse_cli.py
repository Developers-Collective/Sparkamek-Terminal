#----------------------------------------------------------------------

    # Libraries
import os, json
from ..LogType import LogType
from .format_msg import format_msg
from .cmd import press_any_key
from .load_config import load_config
from ..GlobalValues import GlobalValues
from ..cli import CommandResult
#----------------------------------------------------------------------

    # Function
def parse_cli(config_file: CommandResult, add_project: CommandResult = None) -> None:
    config, devkitppc_path = load_config()

    path = os.getcwd()
    os.chdir(GlobalValues.old_path)

    if not os.path.isfile(config_file.path):
        print(format_msg('Unable to find the config file. Please make sure it exists at the given path.', LogType.Error))
        press_any_key()
        return

    with open(config_file.path, 'r', encoding = 'utf8') as f:
        project = json.load(f)
        try: project['path'] = os.path.abspath(project['path'])
        except Exception:
            print(format_msg('Unable to find the project path. Please make sure it exists at the given path.', LogType.Error))
            press_any_key()
            return

    os.chdir(path)

    if add_project is not None:
        existing_projects = [p['name'] for p in config['projects']]
        if project['name'] not in existing_projects:
            with open('./config.json', 'w', encoding = 'utf8') as f:
                config['projects'].append(project)
                json.dump(config, f, indent = 4)
            print(format_msg(f'Added project {project["name"]} to config.json', LogType.Success))
            press_any_key(3)

        else:
            index = existing_projects.index(project['name'])
            old_project = config['projects'][index]
            if old_project != project:
                with open('./config.json', 'w', encoding = 'utf8') as f:
                    config['projects'][index] = project
                    json.dump(config, f, indent = 4)
                print(format_msg(f'Updated project {project["name"]} in config.json', LogType.Success))
                press_any_key(3)

    compile(project, devkitppc_path)
#----------------------------------------------------------------------
