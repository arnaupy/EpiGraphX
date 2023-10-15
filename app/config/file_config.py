import yaml
import os
from rich.progress import track


class CreatingDirectoriesError(Exception):
    """Raised when directories where not created correctly"""

# Get yaml file path
directory_path = os.path.dirname(__file__)
yaml_filename = os.path.basename(__file__).split(".py")[0]
YAML_PATH = f"{directory_path}/{yaml_filename}.yaml"


def read_directories_from_yaml() -> dict[str, str]:
    """Read directory names from a yaml file returning a dict of all the paths to directories"""
    
    def backtrack(parent_dir: str, child_dirs: list[dict], directories: dict[str, str] = {}) -> dict[str, str]:
        """Walks trought directories returning all the directories in the corresponding parent layer"""
        
        for directory_name, sub_directories in child_dirs.items():
            
            # Directory path including parent
            directory_path = "/".join((parent_dir, directory_name))
            
            # If the current directory is not a leave, it bactracks its children directories
            if sub_directories:
                directories = backtrack(child_dirs = sub_directories, parent_dir = directory_path, directories = directories)
            
            else:   
                # Append the directory path to the list of directories if direcotry is a leave
                directories.update({directory_name: directory_path})
            
        return directories
    
    # Open yaml file an its contents in a dictionary
    with open(YAML_PATH, 'r') as yaml_file:
        config_dict = yaml.safe_load(yaml_file)
    
    # Get the root directory and its children directories
    root_directory = config_dict.popitem()
    
    # Bactrack trought every leave returning a directories list and the root directory
    return root_directory[0], backtrack(parent_dir = root_directory[0], child_dirs = root_directory[1])
    
    
def build_directories(directories: dict[str, str]) -> bool:
    """Build paths from a list of directories"""

    # Check if directories are already created
    if all(os.path.isdir(directory_path) for directory_path in directories.values()):
        return "Directories already created"
    
    # Creates directories and intermidiate folders if needed
    directory_leaves = 0
    for directory_path in track(directories.values(), description = "Building directories..."): 
        os.makedirs(directory_path)
        directory_leaves += 1
    
    return f"{directory_leaves} directory leave created"


if __name__ == "__main__":
    
    # Get directories dict specified in the yaml file
    _, directories_to_create = read_directories_from_yaml()
    
    # Build directories
    try:
        build_directories(directories_to_create)
    except:
        raise CreatingDirectoriesError("Directories where not created")
    
    
    


    
    