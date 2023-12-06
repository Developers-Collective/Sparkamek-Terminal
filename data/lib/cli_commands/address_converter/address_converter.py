#----------------------------------------------------------------------

    # Libraries
from ...compiler import AddressMapperController
from ...main_functions import clear, press_any_key
from ...main_functions.logs import log_complete, LogType
#----------------------------------------------------------------------

    # Class
def address_converter(address_mapper_path: str, input_address: int, input_region: str, output_region: str) -> None:
    error: bool = False

    with open(address_mapper_path, 'r', encoding='utf-8') as infile:
        base_address_mapper = AddressMapperController.read_version_info(infile)

    other_address_mapper = AddressMapperController.revert_mappers(base_address_mapper)

    middle_address: int = other_address_mapper[input_region].demap_reverse(input_address)
    if base_address_mapper[input_region].remap(middle_address) != input_address:
        error = True

        #todo: show warning message

    else:
        #todo: show success message
        pass

    output_address: int = base_address_mapper[output_region].remap(middle_address)

    if other_address_mapper[output_region].demap_reverse(output_address) != middle_address:
        error = True

        #todo: show error message

    if not error: pass #todo: show success message
    elif input_address == output_address: pass #todo: show warning message
    else: pass #todo: show error message
#----------------------------------------------------------------------
