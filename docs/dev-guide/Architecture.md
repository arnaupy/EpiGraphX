# How is code structured?
![Arquitecture diagram](../images/CodeArchitecture.png)

## Core
This is the main piece of the code that manages the interaction between the database and backend. It consists of four interconnected parts:

- `Features`: responsible for app functionalities. 
- `Models`: represent storage objects, which can inherit from file systems or any database in `DATABASES`. 
- `Schemas`: represent `Models` sent through the API.
- `Processors`: interact with objects created in models if needed.