import os
from typing import Any
from pathlib import Path


def get_metadata(project_name: str) -> dict[str, Any]:
    if os.environ["BUILDING_ENVIRONMENT"] == "develop":
        import json

        # Load metadata from the project json file
        with open(f"{project_name}.json", "r") as file:
            return json.load(file)

    else:
        import pkg_resources
        import email

        distribution = pkg_resources.get_distribution(project_name)
        metadata = distribution.get_metadata("METADATA")
        metadata = dict(email.message_from_string(metadata))
        metadata = {
            key.lower().replace("-", "_"): value for key, value in metadata.items()
        }

    return metadata


# Get the project name
project_name = Path(__file__).parent.parent.name
metadata = get_metadata(project_name)
