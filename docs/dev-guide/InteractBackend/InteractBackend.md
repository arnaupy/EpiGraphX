# How to interact with the backend?
This project is using `Docker` containers to isolate all app functionalities. To make it easier to interact with images and containers, you can see the [Makefile](../../../Makefile). That file is repossible to run commands using `make` followed by the comand specified in that file.

To see information about make comand, run:
```
make help
```

## Build containers
The following comand creates the corresponding images and build container specified in `Docker files`.
```
make build
```

* This comand will also run the server at port `8080`which you can access with `FastAPI docs` automatically at http://localhost:8080/docs

![App](FastAPI-Docs.png) 

## Run the server
After building containers, you can restart the server:
```
# With logs
make devrun

# In detached mode
make run
```

## Stop & Remove containers
If you runned the server in `detached mode`, you can use the following comand to stop the processes.
```
make stop
```
Moreover, if you want to remove containers, images and volumes:
```
make down
```

