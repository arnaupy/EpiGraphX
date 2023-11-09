# Quick start
Here you'll see a short tutorial to get to know how the backend works. 

Currently, it's only implemeted the `CRUD` feature soo we'll see all the process to follow to get a network registered in the system and how to interact with it.

Make sure you run the following comands:
<div class="annotate" markdown>
```
make create (1)
make run
``` 
</div>

1.  ❗You have to run this comands in case you din't run it before to create containers.


!!! tip
    You can use `FastAPI` tool to do this tutorial. Read [How to interact with the backend](../InteractBackend/InteractBackend.md) to see a quick review of how to use this tool.

## Create network
Use the `Create Network` option and send a `JSON` file, such as:
=== "FastAPI docs"
    ```json
    {
      "label": "EmailEnron",
      "origin": "email-enron-large.txt"
    }
    ```
=== "Terminal"
    ```bash
    curl -X 'POST' \
      'http://localhost:8080/networks/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "label": "EmailEnron",
      "origin": "email-enron-large.txt"
    }'
    ```

Make sure you receive the following response with a different **id**:
```json
{
  "label": "EmailEnron",
  "is_private": true,
  "origin": "email-enron-large.txt",
  "id": "jsl3b6wsqfmmq9v41bbfun88mykhuh",
  "nodes": null,
  "edges": null,
  "is_scanned": false,
  "last_update": "2023-10-03T10:47:57",
  "last_scan": null,
  "time_to_scan": null,
  "degree": null,
  "link": null,
  "pini": null,
  "pfin": null
}
```


## Read network
First, ensure that the network file named in `origin` when creating the network is stored in the system. To do so, you have to upload the network file `email-enron-large.txt` you find in [NetworkFiles](https://github.com/arnaupy/EpiGraphX/tree/develop/NetworkFiles) directory using the `Upload Network File` function. The response body:
=== "FastAPI docs"
    ```json
    {
      "uploaded_file": {
        "filename": "email-enron-large.txt",
        "size": 1804419
      }
    }
    ```

=== "Terminal"
    <div class="annotate" markdown>
    ```bash
    curl -X 'POST' \
      'http://localhost:8080/files/networks' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@NetworkFiles/UniformNetwork.txt;type=text/plain' # (1)! 
    ```
    </div>

    1. ❗ In case you are running the request to the API on the projects' root directory.

Once the network is `registered` in the system and the `network file` is abailable, you can read it by adding the registered **network id** as a parameter to the `Read Network` function. The response will be:
```json
{
  "scanned": true
}
```


## Get network
Now, attempt to retrieve the network table information using the `Get Network` if you wrote down the network id or `Get Networks` in case you forgot to do so:

### By the network id
=== "Fast API docs"
    Simply press the execute comand leaving `skip` to 0 and the `limit` to 100 as default.

=== "Terminal"
    ```bash
    curl -X 'GET' \
      'http://localhost:8080/networks/?skip=0&limit=100' \
      -H 'accept: application/json'
    ```

### By list of network
=== "Fast API docs"
    Simply press execute the comand introducing the network `id`.

=== "Terminal"
    ```bash
    curl -X 'GET' \
      'http://localhost:8080/networks/jsl3b6wsqfmmq9v41bbfun88mykhuh' \
      -H 'accept: application/json'
    ```

If you successfully execute this request, you will receive:
```json
{
  "label": "EmailEnron",
  "is_private": true,
  "origin": "email-enron-large.txt",
  "id": "jsl3b6wsqfmmq9v41bbfun88mykhuh",
  "nodes": 33696,
  "edges": 180811,
  "is_scanned": true,
  "last_update": "2023-10-03T10:58:08",
  "last_scan": "2023-10-03T10:58:08",
  "time_to_scan": "1.246"
}
```

!!! warning
    To get all the data from the network use this operation with the `/data` extention (this option retrieves the four network vectors too).


## Update network
If you entered an incorrect `origin` or wish to modify the `label`, use the `Update Network` functionality. Fill the following JSON file along with the network id:
=== "FastAPI docs"
    ```json
    {
      "label": "othername",
      "origin": "otherfile.txt"
    }
    ```

=== "Terminal"
    ```bash
    curl -X 'PUT' \
      'http://localhost:8080/networks/jsl3b6wsqfmmq9v41bbfun88mykhuh' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "label": "othername",
      "origin": "otherfile.txt"
    }'
    ```

!!! note
    You don't have to update both `label` and `origin` at the same time. If any of these values is the same as the one stored in the database, its values are not updated.

If you don't add a label, it won't be modified, but if you want to update the origin, you must specify if is_private is True or False too. Then, if everything went as expected:
```json
{
  "updates": {
    "label": "EmailEnron -> othername",
    "origin": "email-enron-large.txt -> otherfile.txt"
  }
}
```
!!! note
    Check that the network is correctly updated by retrieving the network once again. 

## Delete network
Finally, you can try to delete the network using the `Delete Network` function by specifying its id. The response will be:
```json
{
    "deleted": true
}
```
