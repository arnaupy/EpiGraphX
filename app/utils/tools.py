import random as rd

def random_id(lenght: int = 30) -> str:
    """method to get random id

    Args:
        lenght (int, optional): lenght od the id. Defaults to 30.

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


def mean(array: list) -> float:
    sumatory = 0
    for entry in array:
        sumatory += entry.item_value
    return sumatory/len(array)