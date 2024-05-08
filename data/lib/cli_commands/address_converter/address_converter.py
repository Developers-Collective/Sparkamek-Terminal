#----------------------------------------------------------------------

    # Libraries
from ...compiler import AddressMapperController
from ...main_functions import clear, press_any_key
from ...main_functions.logs import LogType, log_complete
from ...cli import CLIConstants
#----------------------------------------------------------------------

    # Class
def address_converter(address_mapper_path: str, input_address: int, input_region: str, output_region: str) -> None:
    error: int = 0
    schema_str: str = f'{CLIConstants.FontColor.terminal_color}0x{input_address:08X} ({input_region}){CLIConstants.Reset} => %c%s (Default){CLIConstants.Reset} => %c%s ({output_region}){CLIConstants.Reset}'

    version_ids = {
        'P2': 'pal2',
        'E1': 'ntsc',
        'E2': 'ntsc2',
        'J1': 'jpn',
        'J2': 'jpn2',
        'K': 'kor',
        'W': 'twn',
        'C': 'chn',
    }

    with open(address_mapper_path, 'r', encoding='utf-8') as infile:
        base_address_mapper = AddressMapperController.read_version_info(infile, version_ids)

    other_address_mapper = AddressMapperController.revert_mappers(base_address_mapper)

    middle_address: int = other_address_mapper[input_region].demap_reverse(input_address)
    schema_str = schema_str.replace('%s', f'0x{middle_address:08X}', 1)

    if base_address_mapper[input_region].remap(middle_address) != input_address:
        error += 1

        log_complete(f'Input address (0x{input_address:08X}) cannot be converted to default region.', LogType.Warning)

    output_address: int = base_address_mapper[output_region].remap(middle_address)
    schema_str = schema_str.replace('%s', f'0x{output_address:08X}', 1)

    if other_address_mapper[output_region].demap_reverse(output_address) != middle_address:
        error += 1

        log_complete(f'Default address (0x{middle_address:08X}) cannot be converted to output region.', LogType.Warning)

    print(' ' * 8, end = '')

    if not error:
        print(schema_str.replace('%c', LogType.Success.value.terminal_color, 2))
        log_complete(f'Successfully converted address to output region ({output_region}): {LogType.Success.value.terminal_color}0x{output_address:08X}{CLIConstants.Reset}', LogType.Success)

    elif input_address == output_address:
        print(schema_str.replace('%c', LogType.Warning.value.terminal_color, 2))
        log_complete(f'Input address (0x{input_address:08X}) cannot be converted back and forth with the same region ({input_region}).', LogType.Warning)

    else:
        print(schema_str.replace('%c', LogType.Warning.value.terminal_color if error == 1 else LogType.Error, 1).replace('%c', LogType.Error.value.terminal_color, 1))
        log_complete(f'Input address (0x{input_address:08X}) cannot be converted to output region ({output_region}).', LogType.Error)
#----------------------------------------------------------------------
