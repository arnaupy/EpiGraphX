# Quick start
Here you'll see a short tutorial to get to know how the backend works. 

Currently, it's only implemeted the `CRUD` feature soo we'll see all the process to follow to get a network registered in the system and how to interact with it.

Make sure you have your Docker engine working before running the following comands:
<div class="annotate" markdown>

```
make (1)
make devrun
``` 
</div>

1. Only run this comand ones. This comand create the app containers. Run `make help` for further information.



!!! tip
    You can use `FastAPI` tool to do this tutorial. Read [How to interact with the backend](../InteractBackend/InteractBackend.md) to see a quick review of how to use this tool.

## Create network
Use the `Create Network` option and send a `JSON` file, such as:
=== "FastAPI docs"
    ```json
    {
      "label": "Tutorial Network",
      "origin": "UniformNetwork.txt"
    }
    ```
=== "Terminal"
    ```bash
    curl -X 'POST' \
      'http://localhost:8080/networks/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "label": "Tutorial Network",
      "origin": "UniformNetwork.txt"
    }'
    ```

Make sure you receive the following response with a different **id**:
```json
{
  "label": "Tutorial Network",
  "origin": "UniformNetwork.txt",
  "is_private": true,
  "id": "04777838-32b1-4332-8a58-1e303ac2abb9",
  "nodes": null,
  "edges": null,
  "is_scanned": false,
  "last_update": "2024-01-25T01:47:51",
  "last_scan": null,
  "time_to_scan": null,
  "degree": null,
  "link": null,
  "pini": null,
  "pfin": null
}
```


## Scan network
First, ensure that the network file named in `origin` when creating the network is stored in the system. To do so, you have to upload the network file `UniformNetwork.txt` you find in [NetworkExample](https://github.com/arnaupy/EpiGraphX/tree/main/tests/) directory using the `Upload Network File` function.

=== "FastAPI docs"
    Simply follow the api documentation instructions.

=== "Terminal"
    <div class="annotate" markdown>
    ```bash
    curl -X 'POST' \
      'http://localhost:8080/files/networks' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@UniformNetwork.txt;type=text/plain' # (1)! 
    ```
    </div>

    1. ❗ Make sure to specify the correct file path. 

The response body:
```json
{
  "uploaded_file": {
    "filename": "UniformNetwork.txt",
    "size": 2500000
  }
}
```

Once the network is `registered` in the system and the `network file` is abailable, process by scanning the network.

=== "FastAPI docs"
    Add the registered **network id** as a parameter to the `Scan Network` function.

=== "Terminal"
    <div class="annotate" markdown>
    ```bash
    curl -X 'PATCH' \
    'http://localhost:8080/networks/04777838-32b1-4332-8a58-1e303ac2abb9' \ # (1)!
    -H 'accept: application/json'
    ```
    </div>

    1. Place the corresponding network id. 

The response body:
```json
{
  "scanned": true
}
```

## Get network
Now, attempt to retrieve the network table information using the `Get Network` if you wrote down the network id or `Get Networks` in case you forgot to do so:

### Listing networks
=== "Fast API docs"
    Simply press the execute comand leaving `skip` to 0 and the `limit` to 100 as default.

=== "Terminal"
    ```bash
    curl -X 'GET' \
      'http://localhost:8080/networks/?skip=0&limit=100' \
      -H 'accept: application/json'
    ```

### Get by network id
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
  "label": "Tutorial Network",
  "origin": "UniformNetwork.txt",
  "is_private": true,
  "id": "04777838-32b1-4332-8a58-1e303ac2abb9",
  "nodes": 10000,
  "edges": 100000,
  "is_scanned": true,
  "last_update": "2024-01-25T01:59:36",
  "last_scan": "2024-01-25T01:59:36",
  "time_to_scan": "0.229"
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
      'http://localhost:8080/networks/04777838-32b1-4332-8a58-1e303ac2abb9' \
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
    "label": "Tutorial Network -> othername",
    "origin": "UniformNetwork.txt -> otherfile.txt"
  }
}
```
!!! note
    Check that the network is correctly updated by retrieving the network once again. 

## Delete network
Finally, you can try to delete the network using the `Delete Network` function.
=== "FastAPI docs"
    Specifying the network `id`.

=== "Terminal"
    ```bash
    curl -X 'DELETE' \
      'http://localhost:8080/networks/04777838-32b1-4332-8a58-1e303ac2abb9' \
      -H 'accept: application/json'
    ```

The corresponding response:
```json
{
    "deleted": true
}
```
