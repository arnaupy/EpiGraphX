from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

PRIVATE_LABEL = "UniformNetwork"
UPDATED_LABEL = "OtherUniformNetwork"
PRIVATE_NODES = 10000
PRIVATE_EDGES = 100000
PRIVATE_NETWORK_FILE = "UniformNetwork.txt"
UPDATED_PRIVATE_NETWORK_FILE = "OtherUniformNetwork.txt"
PRIVATE_FILE_SIZE = 2500000
NUMPY_INT_TYPE = "int32"

def test_create_private_network():
    
    response = client.post(
        "/networks/",
        json = {"label": PRIVATE_LABEL, "origin": PRIVATE_NETWORK_FILE},
    )
    
    assert response.status_code == 200, response.text
    
    data = response.json()
    assert type(data["id"]) == str
    assert data["label"] == PRIVATE_LABEL
    assert data["is_private"] == True
    assert data["origin"] == PRIVATE_NETWORK_FILE
    assert data["nodes"] == None
    assert data["edges"] == None 
    assert data["is_scanned"] == False
    assert type(data["last_update"]) == str 
    assert data["last_scan"] == None
    assert data["time_to_scan"] == None
    assert data["degree"] == None
    assert data["link"] == None
    assert data["pini"] == None
    assert data["pfin"] == None
    
    
    
    response = client.post(
        "/networks/",
        json = {"label": PRIVATE_LABEL, "origin": PRIVATE_NETWORK_FILE},
    )
    assert response.status_code == 400, response.text

def test_upload_file():
    
    with open(PRIVATE_NETWORK_FILE, "rb") as f:
        response = client.post("/files/networks", files = {"file": (PRIVATE_NETWORK_FILE, f, "image/jpeg")})
        assert response.status_code == 200, response.text
        data = response.json()
        file = data["uploaded_file"]

        assert file["filename"] == PRIVATE_NETWORK_FILE
        assert file["size"] == PRIVATE_FILE_SIZE
        

def test_scan_private_network():
    
    response = client.get(
        "/networks/",
        params = {"skip": 0, "limit": 1}
    )
    id = response.json()["id"]

    response = client.patch(f"/networks/{id}")
    assert response.status_code == 200, response.text
    
    data = response.json()
    assert data == {'scanned': True}
    
    
    response = client.get(f"/networks/{id}/data")
    assert response.status_code == 200, response.text
    
    data = response.json()
    assert type(data["id"]) == str
    assert data["label"] == PRIVATE_LABEL
    assert data["is_private"] == True
    assert data["origin"] == PRIVATE_NETWORK_FILE
    assert data["nodes"] == PRIVATE_NODES
    assert data["edges"] == PRIVATE_EDGES
    assert data["is_scanned"] == True
    assert data["last_update"] == data["last_scan"] 
    assert type(data["last_update"]) == str
    assert type(data["time_to_scan"]) == str
    
    degree = data["degree"]
    assert degree["dtype"] == NUMPY_INT_TYPE
    assert len(eval(degree["array"])) == PRIVATE_NODES
    
    link = data["link"]
    assert link["dtype"] == NUMPY_INT_TYPE
    assert len(eval(link["array"])) == 2*PRIVATE_EDGES
    
    pini = data["pini"]
    assert pini["dtype"] == NUMPY_INT_TYPE
    assert len(eval(pini["array"])) == PRIVATE_NODES

    pfin = data["pfin"]
    assert pfin["dtype"] == NUMPY_INT_TYPE
    assert len(eval(pfin["array"])) == PRIVATE_NODES


def test_update_network():

    response = client.get(
        "/networks/",
        params = {"skip": 0, "limit": 1}
    )
    id = response.json()["id"]
    
    response = client.put(
        f"/networks/{id}",
        json = {"label": UPDATED_LABEL}
        )
    assert response.status_code == 200, response.text
    
    data = response.json()
    
    assert len(data) == 1
    assert data["updates"] == {"label": f"{PRIVATE_LABEL} -> {UPDATED_LABEL}"}
    
    response = client.get(f"/networks/{id}")
    assert response.status_code == 200, response.text
    
    data = response.json()
    assert data["label"] == UPDATED_LABEL
    

    response = client.put(
        f"/networks/{id}",
        json = {"origin": UPDATED_PRIVATE_NETWORK_FILE}
        )
    assert response.status_code == 200, response.text
    
    data = response.json()
    
    assert len(data) == 1
    assert data["updates"] == {"origin": f"{PRIVATE_NETWORK_FILE} -> {UPDATED_PRIVATE_NETWORK_FILE}"}
    
    response = client.get(f"/networks/{id}")
    assert response.status_code == 200, response.text
    
    data = response.json()
    assert data["origin"] == UPDATED_PRIVATE_NETWORK_FILE
    
    