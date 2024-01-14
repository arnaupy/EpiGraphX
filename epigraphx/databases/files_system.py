import os

ROOT: str = "./files"
NETWORK_FILE: dict = {
    "directory": os.path.join(ROOT, "networks"),
    "extensions": ["txt", "edges"]
}
    
def create_files_system() -> None: 
    os.makedirs(NETWORK_FILE["directory"], exist_ok=True)
