#----------------------------------------------------------------------
    # Function
def rreplace(s: str, old: str, new: str, count: int) -> str:
    '''Replace the last occurrence of a substring in a string.
    
    Args:
        s (str): The string to be processed.
        old (str): The substring to be replaced.
        new (str): The new substring.
        occurrence (int): The number of occurrences to replace.
    
    Returns:
        str: The new string with the replaced substring.
    
    Example:
        >>> rreplace('foo bar foo', 'foo', 'baz', 1)
        'foo bar baz'
    '''

    return new.join(s.rsplit(old, count))
#----------------------------------------------------------------------
