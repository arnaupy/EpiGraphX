"""   
    FUNCTIONS:
    |
    |   * get_path -> get the full file path from root
    |
    |       inputs:
    |           - *args(tuple(str)): tuple of directories and/or file to join
    |        
    |       outputs -> (str): file path including the root
    +
"""

def get_path(directory: str, filename: str) -> str:
    """Joins directories and/or a file in a single path"""
    return "/".join((directory, filename))