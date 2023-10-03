# What are the main functionalities that must be managed by the app?
The app must have some essential functionalities before starting to add any research like tool.

## CRUD implementation
CRUD accounts for `Create & Read & Update & Delete` features. In the app context, the first object that can be ruled that way is a `network`. Then we'll see what means each CRUD feature for networks.

- Create -> register a network entry in the database. 
- Read -> `get` network data from the database
- Update -> change `label` and `origin` features from network. Also in this context, it means to `scan` the network and storing its data according to the database structure ([DATABASE](DATABASE.md)).
- Delete -> since the four vector that defines the network are related to it, this table entries must be deleted before delting the network entry in its table.


