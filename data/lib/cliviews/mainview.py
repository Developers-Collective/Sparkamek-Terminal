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
    # Setup
    cli_ = CLI(
        executable,
        f'{CLIConstants.VersionTitleColor.terminal_color}Sparkamek Terminal'
        f'{CLIConstants.VersionSeparatorColor.terminal_color} | '
        f'{CLIConstants.VersionDigitColor.terminal_color}{VERSION[0]}'
        f'{CLIConstants.VersionSeparatorColor.terminal_color} • '
        f'{CLIConstants.VersionDigitColor.terminal_color}{VERSION[1]}'
        f'{CLIConstants.Reset}'
    )


    # Help
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
            description = 'Show this help message and exit.',
            aliases = ('-h', '--help'),
            arguments = (Argument('command', ArgumentType.Optional),)
        ),
    )
    help_section_group.add_section(help_section)


    # Version
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
            description = 'Show the version and exit.',
            aliases = ('-v', '--version')
        ),
    )
    version_section_group.add_section(version_section)


    # Compile
    compile_choice = Choice(
        name = 'options',
        callback = lambda **kwargs: callback(**kwargs)
    )
    cli_.add_choice(compile_choice)

    compile_section_group = SectionGroup(
        'project-options',
    )
    compile_choice.add_section_group(compile_section_group)

    compile_options_section = Section(
        'project-options',
        SectionType.Optional,
        Command(
            name = 'add-project',
            description = 'Add a project to the config file if it doesn\'t exist.',
            aliases = ('-a', '--add-project'),
            # arguments = (Argument('name', ArgumentType.Mandatory), Argument('path', ArgumentType.Mandatory))
        )
    )
    compile_section_group.add_section(compile_options_section)

    config_file = Section(
        'config-file',
        SectionType.Mandatory,
        Command(
            name = 'config-file',
            description = 'Path to the JSON config file.',
            aliases = ('-cf', '--config-file'),
            arguments = (Argument('path', ArgumentType.Mandatory),)
        )
    )
    compile_section_group.add_section(config_file)


    # Address Converter
    address_converter_choice = Choice(
        name = 'address-converter',
        callback = lambda **kwargs: print(kwargs)
    )
    cli_.add_choice(address_converter_choice)

    address_converter_section_group = SectionGroup(
        'address-converter',
    )
    address_converter_choice.add_section_group(address_converter_section_group)

    address_mapper_section = Section(
        'address-mapper-path',
        SectionType.Optional,
        Command(
            name = 'address-mapper-path',
            description = 'Path to the address mapper file. If not specified, the default address mapper will be used.',
            aliases = ('-amp', '--address-mapper-path'),
            arguments = (Argument('path', ArgumentType.Mandatory),)
        ),
    )
    address_converter_section_group.add_section(address_mapper_section)

    address_converter_section = Section(
        'address-converter',
        SectionType.Mandatory,
        Command(
            name = 'address-converter',
            description = 'Convert an address from one region to another. Addresses must be in hexadecimal format.',
            aliases = ('-ac', '--address-converter'),
            arguments = (
                Argument('input-address', ArgumentType.Mandatory),
                Argument('input-region', ArgumentType.Mandatory),
                Argument('output-region', ArgumentType.Mandatory),
            )
        ),
    )
    address_converter_section_group.add_section(address_converter_section)


    # Execute
    cli_.exec(*sys.argv[1:])
#----------------------------------------------------------------------
