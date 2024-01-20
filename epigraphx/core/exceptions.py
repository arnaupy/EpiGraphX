class InvalidFileExtension(Exception):
    """Raises when the file name missmatches the class extention"""


class InvalidStringFormat(Exception):
    """Raises when the string format of the mapped type variable is not correct"""


class SizeMissmatchError(Exception):
    """Raises when the size of the array missmatches the array length"""


class NetworkOriginError(Exception):
    """Raises when the origin of a network is incorrect"""
