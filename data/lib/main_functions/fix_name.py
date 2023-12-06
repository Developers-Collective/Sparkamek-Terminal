#----------------------------------------------------------------------

    # Libraries
def fix_name(name: str) -> str:
    authorized = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    new_name = ''.join([char if char in authorized else '_' for char in name])
    if new_name[0] in '0123456789': new_name = '_' + new_name

    return new_name
#----------------------------------------------------------------------
