#----------------------------------------------------------------------

    # Libraries
import sys
from data.lib.cli import *
from data.lib.version import VERSION
from typing import Callable
from data.lib.cli.CLIConstants import CLIConstants
#----------------------------------------------------------------------

    # Functions
def mainview(executable: str, callback: Callable):
    cli_ = CLI(
        executable,
        f'{CLIConstants.VersionTitleColor.terminal_color}Sparkamek Terminal'
        f'{CLIConstants.VersionSeparatorColor.terminal_color} | '
        f'{CLIConstants.VersionDigitColor.terminal_color}{VERSION[0]}'
        f'{CLIConstants.VersionSeparatorColor.terminal_color} • '
        f'{CLIConstants.VersionDigitColor.terminal_color}{VERSION[1]}'
        f'{CLIConstants.Reset}'
    )


    help_choice = Choice(
        name = 'help',
        callback = cli_.display,
    )
    cli_.add_choice(help_choice)

    help_section_group = SectionGroup(
        'Help',
    )
    help_choice.add_section_group(help_section_group)

    help_section = Section(
        'help',
        SectionType.Mandatory,
        Command(
            name = 'help',
            description = 'Show this help message and exit',
            aliases = ('-h', '--help'),
            arguments = (Argument('command', ArgumentType.Optional),)
        ),
    )
    help_section_group.add_section(help_section)


    version_choice = Choice(
        name = 'version',
        callback = lambda version: print(cli_.version)
    )
    cli_.add_choice(version_choice)

    version_section_group = SectionGroup(
        'Version',
    )
    version_choice.add_section_group(version_section_group)

    version_section = Section(
        'version',
        SectionType.Mandatory,
        Command(
            name = 'version',
            description = 'Show version and exit',
            aliases = ('-v', '--version')
        ),
    )
    version_section_group.add_section(version_section)


    options_choice = Choice(
        name = 'options',
        callback = lambda **kwargs: callback(**kwargs)
    )
    cli_.add_choice(options_choice)

    options_section_group = SectionGroup(
        'Options',
    )
    options_choice.add_section_group(options_section_group)

    options_section = Section(
        'options',
        SectionType.Optional,
        Command(
            name = 'add-project',
            description = 'Add a project to the config file if it doesn\'t exist',
            aliases = ('-a', '--add-project'),
            # arguments = (Argument('name', ArgumentType.Mandatory), Argument('path', ArgumentType.Mandatory))
        )
    )
    options_section_group.add_section(options_section)

    config_file = Section(
        'config-file',
        SectionType.Mandatory,
        Command(
            name = 'config-file',
            description = 'Path to the config file',
            aliases = ('-cf', '--config-file'),
            arguments = (Argument('path', ArgumentType.Mandatory),)
        )
    )
    options_section_group.add_section(config_file)

    cli_.exec(*sys.argv[1:])
#----------------------------------------------------------------------
