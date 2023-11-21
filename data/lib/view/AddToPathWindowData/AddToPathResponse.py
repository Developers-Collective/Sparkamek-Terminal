#----------------------------------------------------------------------

    # Libraries
from enum import Enum
#----------------------------------------------------------------------

    # Class
class AddToPathResponse(Enum):
    Yes = ('Yes', 'yes')
    No = ('No', 'no')
    NoAndDontAskAgain = ('No, and don\'t ask again', 'no_and_dont_ask_again')

    def from_str(string: str) -> 'AddToPathResponse':
        for response in AddToPathResponse:
            if string in response.value: return response
        raise ValueError(f'Unknown response: {string}')
#----------------------------------------------------------------------
