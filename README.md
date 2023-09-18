# EpiGraphX


App to simulate Epidemics on Networks.

## Introduction

In June 2023, I successfully completed my undergraduate thesis as an aspiring physicist. The aim of this project is to expand upon and refine the work I developed over the course of approximately four months.

You can find the paper I wrote about the thesis on my [LinkedIn](https://www.linkedin.com/in/arnau-perez-perez/) profile.


## How to run the app?

This project is built upon `Docker` containers to isolate all dependencies and access `Fortran` subroutines for the most computationally demanding functions thanks to [f2py](https://numpy.org/doc/stable/f2py/). You can review the [Fortran](./docs/fortran) functions I employed in my thesis.

The following command builds the app and the `PostgreSQL` database images and containers. All container configurations are specified in [DockerFile.dev](./Dockerfile.dev) and [docker-compose-dev.yml](./docker-compose-dev.yml).
```
docker compose -f docker-compose-dev.yml up --build
```
To restart the app simply run the same command omitting `--build`. You can add the `-d` parameter if you don't want to see what the container is managing in the background (`FastAPI` requests).

To interact with the app, please keep in mind that the app is running on container port **80**, which can be accessed from the local machine on port **8080**. I strongly recommend using FastAPI docs to familiarize yourself with the app once it's running (http://localhost:8080/docs).

![App](./docs/images/AppDocs.png) 

## Features
### CRUD
At the moment, the app is only capable of creating, reading, updating, and deleting a network. ([crud.py](./app/crud.py) | [view.py](./app/view.py) | [main.py](./app/main.py))

## Quick start
First, note that the app stores network files in the `network` directory inside the container, sourced from the local machine, located in [docs](./docs/networks/). Every functionality presented here can be tested in various ways, but as mentioned earlier, FastAPI docs is one of the best options for doing so.

---
### Create network
Use the `Create Network` option and send a JSON file, such as:
```
{
    "label":"UniformNetwork",
    "file_path":"networks/UniformNetwork.txt"
}
```
Make sure you receive the following response with a different **id**:
```
{
    "label": "UniformNetwork",
    "file_path": "networks/UniformNetwork.txt",
    "id": "sl98g96npuke0xy2wg3tbqcs0vb8rh",
    "nodes": null,
    "edges": null,
    "is_read": false,
    "degree": [],
    "link": [],
    "pini": [],
    "pfin": []
}
```

---
### Read network
Once the network is registered, you can read it by adding the registered **network id** as a parameter to the `Read Network` function. The response will be:
```
{
  "scanned": true
}
```

---
### Get network
Now, attempt to retrieve the network table information using the `Get Network` operation. If you are using the **FastAPI docs**, please avoid performing this operation with the `/data` path, or you'll need to refresh the page :scream: (using this option retrieves the four network vectors). If you successfully execute this request, you will receive:
```
{
    "label": "UniformNetwork",
    "file_path": "networks/UniformNetwork.txt",
    "id": "sl98g96npuke0xy2wg3tbqcs0vb8rh",
    "nodes": 10000,
    "edges": 100000,
    "is_read": true
}
```

---
### Update network
If you entered an incorrect `file_path` or wish to modify the `label`, use the `Update Network` functionality. Fill the following JSON file along with the network id:
```
{
    "label": "new_label",
    "file_path": "new_file_path.txt"
}
```
If you left the default value for **label** and **file_path** (`None`), this features won't be updated. Then, if everything went as expected:
```
{
    "updated": true
}
```
Check that the network is correctly updated by retrieving the network once again.

---
### Delete network
Finally :sweat:, you can try to delete the network using the `Delete Network` function by specifying its id. The response will be:
```
{
    "deleted": true
}
```

## Next steps and improvements
- Transform table arrays into numpy arrays
- Network properties
    - `mean degree`, `mean degree square`, `shortest path`, ...   
- Spreading models
    - `SI`, `SIS`, `SIR`, `SEIR`, `SIRS`, ... 
- Optimize reading process
- Network storage
    - access **.txt** network files using `Git lfs`?
    - using NoSQL databases?

## Contributing
Before starting to develop new features, you must understand how networks are handled in this project. ([How networks are read and stored in the database?](./docs/NETWORKS.md)). Make sure you have `Docker` installed ([How to install Docker?](https://docs.docker.com/engine/install/)). Read `How to run the app?` and make the short `Quick start` if you are new working with **FastAPI**. 

Then, simply clone this repository to your local machine and begin working on `Next steps and improvements` or assist with app documentation in [README](./README.md) and [NETWORKS](./docs/NETWORKS.md).
```
git clone https://github.com/arnaupy/EpiGraphX.git
```
Finally, don't forget to have fun contributing in such an ambicious project :grin:.

Feel free to make any pull request or contact me with any questions or new ideas at -> 01arnauperez@gmail.com

## Goal
Build an app to simulate and study disease spreading processes in networks, with the aim of investigating possible strategies to combat or limit the spread of diseases.

