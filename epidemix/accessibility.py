from utils.base import Session
from network_encoder import Network

class NetworkList:
    def __init__(self):
        pass
    def __repr__(self) -> str:
        pass

def list_networks() -> list:
    """(list_networks)

    Returns:
        list: contains every network registered in the system
    """
    with Session() as session:
        result = session.query(Network).all()
    print(f"(200 OK): Showing networks registered in the system!")
    return result
