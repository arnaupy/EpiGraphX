import os
import yaml
import json
from setuptools import setup, Extension, find_packages


class CMakeExtension(Extension):
    def __init__(self, name, sources=[]):
        super().__init__(name, sources=sources)


def compile_cpp_modules(dirpath: str) -> list[CMakeExtension]:
    # logger.info("Building cpp modules")

    # Load the config file
    cpp_modules_config_filepath = os.path.join(dirpath, "config.yml")
    with open(cpp_modules_config_filepath, "r") as file:
        config = yaml.safe_load(file)

    def compile(source_file: str, shared_file: str) -> None:
        cpp_command = " ".join(
            [
                config["compiler"],
                *config["arguments"],
                *config["includes_dir"],
                source_file,
                "-o",
                shared_file,
                *config["libraries"],
            ]
        )
        # logger.debug(cpp_command)
        os.system(cpp_command)

    # Instanciate the external modules to store cpp modules
    ext_modules: list[CMakeExtension] = []

    for module_name, module_files in config["modules"].items():
        # logger.info(f"{module_name}...")
        # Create the modules directory
        module_dir = os.path.join(dirpath, config["package_name"], module_name)
        os.makedirs(module_dir, exist_ok=True)

        for module_file in module_files:
            # logger.info(module_file)
            # Instanciate source file
            source_file = os.path.join(
                dirpath, config["source_directory"], f"{module_file}.cpp"
            )

            # Instanciate shared filename
            shared_file = os.path.join(module_dir, f"{module_file}.so")

            # Compile cpp scripts
            compile(source_file, shared_file)

            # Append the external modules list
            ext_modules.append(
                CMakeExtension(
                    f"{config['package_name']}.{module_name}.{module_file}",
                    sources=[source_file],
                )
            )

    return ext_modules


def main():
    # Build cpp modules
    ext_modules = compile_cpp_modules("cpp")

    if os.environ["BUILDING_ENVIRONMENT"] in ["production", "test"]:
        # Load metadata from the project json file
        with open("epigraphx.json", "r") as project_file:
            metadata = json.load(project_file)

        # Load README file
        with open("README.md", "r") as readme_file:
            long_description = readme_file.read()

        setup(
            name=metadata["name"],
            description=metadata["description"],
            long_description=long_description,
            version=metadata["version"],
            author=metadata["author"],
            author_email=metadata["author_email"],
            packages=find_packages(),
            ext_modules=ext_modules,
            zip_safe=False,
            license=metadata["license"],
        )


if __name__ == "__main__":
    main()
