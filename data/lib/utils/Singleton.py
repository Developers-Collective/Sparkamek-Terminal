#----------------------------------------------------------------------------------------------------

    # Libraries
from typing import Callable
#----------------------------------------------------------------------------------------------------

    # Class
class Singleton(type):
    '''This is a metaclass which can be used to create a Singleton class.
    ```py
    class MyClass(metaclass = Singleton):
        pass
    ```'''

    _instances = {}

    def __call__(cls, *args, **kwargs) -> object:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



def singleton(cls):
    class class_w(cls):
        _instance = None

        def __new__(cls, *args, **kwargs) -> Callable:
            if class_w._instance is None:
                class_w._instance = super(class_w, cls).__new__(cls, *args, **kwargs)
                class_w._instance._sealed = False
            return class_w._instance

        def __init__(self, *args, **kwargs) -> None:
            if self._sealed:
                return

            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True

    class_w.__name__ = cls.__name__
    return class_w
#----------------------------------------------------------------------------------------------------
