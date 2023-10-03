import random as rd
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta

def random_id(lenght: int = 30) -> str:
    """Method to get a random id

    Args:
        lenght (int, optional): id length. Defaults to 30.

    Returns:
        str: id
    """
    letters = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    caracters = letters + numbers
    id_str = ""
    for _ in range(lenght):
        id_str += rd.choice(caracters)
    return id_str

def now(dateformat: str) -> str:
    """Return the actual string datetime according to the input format"""
    
    return datetime.now().strftime(dateformat)



