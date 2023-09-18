import random as rd
from fastapi.encoders import jsonable_encoder

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


def get_parent(child, parent_class):
    """Method to build a 'parent-pydantic-BaseModel' class from its child. 
       That way getting rid of extra child attributes.

    Args:
        child (BaseModel Instance): child instance
        parent_class (BaseModel Class): parent class

    Returns:
        BaseModel Instance: Parent instance build from shared child attributes 
    """
    parent_attributes = {}
    # Looks for shared attributes between parent and child
    for attribute in jsonable_encoder(child):
        if attribute in parent_class.model_json_schema()["properties"]:
            parent_attributes.update({attribute: jsonable_encoder(child)[attribute]})
    return parent_class(**parent_attributes)
