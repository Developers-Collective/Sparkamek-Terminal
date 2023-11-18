#----------------------------------------------------------------------

    # Libraries
import os
#----------------------------------------------------------------------

    # Function
def press_any_key(time: int = -1) -> None:
    if time < 0: os.system('bash -c \'read -s -n 1 -p "Press any key to continue..."\'')
    else: os.system(f'bash -c \'read -s -t {time} -n 1 -p "Press any key to continue..."\'')

def clear() -> None:
    os.system('clear')
#----------------------------------------------------------------------
