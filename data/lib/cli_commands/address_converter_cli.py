#----------------------------------------------------------------------

    # Libraries
import os
from ..LogType import LogType
from ..main_functions.format_msg import format_msg
from ..cli import CommandResult
from ..compiler.KamekConstants import KamekConstants
from .address_converter.address_converter import address_converter as address_converter_func
#----------------------------------------------------------------------

    # Function
def address_converter_cli(address_converter: CommandResult, address_mapper_path: CommandResult = None) -> None:
    path = address_mapper_path.path if address_mapper_path else KamekConstants.GlobalVersionsNSMBW

    if not os.path.isfile(path):
        return print(format_msg('Invalid address mapper path.', LogType.Error))
    
    addr = address_converter.input_address.lower()
    if addr.startswith('0x'): addr = addr[2:]
    try: addr = int(addr, 16)
    except ValueError:
        return print(format_msg('Invalid input address.', LogType.Error))

    try:
        address_converter_func(path, addr, address_converter.input_region, address_converter.output_region)

    except KeyError as e:
        return print(format_msg(f'Invalid region: {e}', LogType.Error))
#----------------------------------------------------------------------
