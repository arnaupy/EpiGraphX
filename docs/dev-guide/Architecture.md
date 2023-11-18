# How is code structured?
The app is structured with a specific number of layers to ensure that the code is `expandable` and `easily fixable` if necessary. For this reason, the project is divided into four different blocks that are interconnected.

![Arquitecture diagram](../assets/CodeArchitecture.png)

## Core
This is the main piece of the code that manages the interaction between the database and backend. It consists of four interconnected parts:

- `Features` : responsible for app functionalities. 
- `Models` : represent storage objects, which can inherit from file systems or any database in `DATABASES`. 
- `Schemas` : represent `Models` sent through the API.
- `Processors` : interact with objects created in models if needed.

## Routers
This part manages the API paths. 

- `Networks` : contains all the crud functionalities and network features.
- `Files` : contains any system file that can be accessed by the user.

## Databases
The app needs some databases to store the network data or models performance for example. Then, APIs to interact with these databeses are managed in this part of the app.

- `PostgreSQL` : SQL database for storing relational data and data that needs to be modified recurrently or accessed easily.

## View
👷 Work in progress...
