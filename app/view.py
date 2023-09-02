from . import schemas
import numpy as np
from .utils.tools import mean


def describe_network(network: schemas.Network) -> dict:
    return {
        "label": network.label,
        "nodes": network.nodes,
        "edges": network.edges,
        "mean_degree": mean(network.degree)
    }