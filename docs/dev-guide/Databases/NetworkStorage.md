# How is the database structured?
The whole project is based on networks. For that reason, there must be away to encode netowkr data in some way that it can be quickly read for comupations and extended for new properties.

## What database to use?
Due to the large data size coming from networks, the most apropiate database has to be be divisible in smaller part so bigger size data is not afected when managing smaller ones. For that reason the ideal database type is a relational database `SQL`. 

There are lots of relational databases. For the moment, the choosen one is `PostgreSQL`. 

## Where to get networks from?
There are different ways to get data from, but the essential part is that it must be read from somekind of rows and columns file. Why? Networks are described as a graph $G$, composed of a set of nodes, $N$, and edges, $E$, connecting them. In this kind of file, every column correspon to a node and the resulting rows are mapped into edges. From now, where are only talking about graphs that matches the following properties: 

* Nodes are not connected to themselves | `Simple Graph`
* Edges don't have a privileged direction | `Undirected Graph`
* Edges don't have weights | `Non-Weighted Graph`
* There are no isolated nodes | `Connected Graph`

!!! example
    <center>

    | Col1  | Col2  |         Edge         |
    | :---: | :---: | :------------------: |
    |  $1$  |  $4$  | $\langle 1,4\rangle$ |
    |  $4$  |  $2$  | $\langle 4,2\rangle$ |
    |  $2$  |  $3$  | $\langle 2,3\rangle$ |
    |  $3$  |  $4$  | $\langle 3,4\rangle$ |

    </center>

    In this example we can define the network as a graph $G = (V,E)$, where $E = (\langle 1,4\rangle, \langle 4,2\rangle, \langle 2,3\rangle, \langle 3,1\rangle)$ and $N = (1,2,3,4)$. Since this graph is undirected, the edges set is build of elements represented as $\langle , \rangle$. Nodes can be interchanged and the meaning would be the same.

!!! note    
    Finally, from now, this kind of data can be read by `txt` files. 

## Where to find network files and how to store them?
This txt files can be imported from two different soureces. The `client` can update this files into the internal server storage or request it from `network data repositories`. Then to keep track of client updated files, the text file name should be stored so that the client knows where the data was taken from. Then, id the client requested the data from a repository, the corresponfing url will be saved.



|                  Method                  |  Storing  |                     Example                     |
| :--------------------------------------: | :-------: | :---------------------------------------------: |
|         `Updated` by the client          | file name |               UniformNetwork.txt                |
| `Requested` from network data repository |    url    | https://www.network-data-repository/network.txt |


## How to scan network data?
Once the network file is abailable, its time to process and store its data into the `PostgreSQL` database in the most accessible and efficiently way for later computations. To do that, the network must be stored in `four` different vectors. 

<center>

| **Vector** | **Dim** |                      **Description**                       |
| :--------: | :-----: | :--------------------------------------------------------: |
|   Degree   |   $n$   |                   $D(N_1), ... , D(N_n)$                   |
|    Link    |  $2e$   | $E_1(N_1), ... , E_j(N_1), ... , E_1(N_n), ... , E_1(N_n)$ |
|    Pini    |   $n$   |        $1, pos(E_j(N_1)) + 1, ... , pos(E_1(N_n))$         |
|    Pfin    |   $n$   |                 $pos(E_j(N_1)), ... , 2·e$                 |



|     Symbol      |                               Description                                |
| :-------------: | :----------------------------------------------------------------------: |
|       $n$       |                                 $\|N\|$                                  |
|       $e$       |                                 $\|E\|$                                  |
|    $D(N_i)$     |       Number of edges connecting a node with the target node $N_i$       |
|   $E_i(N_j)$    |         $N_i$   node connecting $N_j$, where $(N_i, N_j) \in E$          |
| $pos(E_i(N_j))$ | Maps the corresponding $E_i(N_j)$ to the position in the **Link** vector |

</center>

That way, network data can be used more efficiently for computation. Then using the same example in `Where to find network files and how to store them?` section, data will be stored as follows:

!!! example
    <center>

    | Col1  | Col2  | Vector |           Value            |
    | :---: | :---: | :----: | :------------------------: |
    |  $1$  |  $4$  | Degree |       $(1, 2, 2, 3)$       |
    |  $4$  |  $2$  |  Link  | $(2, 3, 4, 2, 4, 1, 2, 3)$ |
    |  $2$  |  $3$  |  Pini  |       $(1, 2, 4, 6)$       |
    |  $3$  |  $4$  |  Pfin  |       $(1, 3, 5, 8)$       |

    </center>

## How to store the encoded network into the database?
To sum up, there is a `file name` or `url` assocciated with the database. Two numeric values, the number of `nodes`, $n$, and  the number of `edges`, $e$. Finally, we heave `four vectors` that define the structure of the network. Then, to store all this data we need `five SQL tables`:

=== "Network"
    <center>

    |    Column    	|                                        Description                                       	|   Dtype  	| Optional 	|
    |:------------:	|:----------------------------------------------------------------------------------------:	|:--------:	|:--------:	|
    |      `id`      	|                                          unic id                                         	|    str   	|   False  	|
    |     `label`    	|                                    name of the network                                   	|    str   	|   False  	|
    |    `origin`   	|                                 network file name \| url                                 	|    str   	|   False  	|
    |  `is_private` 	| whether the network was `requested`(= False) by an url or `updated`(= True) by the user  	|   bool   	|   False  	|
    |    `is_scanned`  	|                whether the network have been read from the file and stored               	|   bool   	|   False  	|
    |     `nodes`    	|                                          $\|N\|$                                         	|    int   	|   True   	|
    |     `edges`   	|                                          $\|E\|$                                         	|    int   	|   True   	|
    |  `last_update` 	|              time when the network `label` or `origin` columns where updated             	| datetime(str) 	|   False   	|
    |   `last_scan`  	|                              last time the network was read                              	| datetime(str) 	|   True   	|
    | `time_to_scan` 	|                        the time it took the encoder to read the network in `sec`                      	| str 	|   True   	|

    </center>

=== "Degree & Link & Pini & Pfin"
    <center>

    |   Column   	|                   Description                  	| Dtype 	| Optional 	|
    |:----------:	|:----------------------------------------------:	|:-----:	|:--------:	|
    |     `id`   	|                     unic id                    	|  str  	|   False  	|
    | `network_id`	|         network id from `network table`        	|  str  	|   False  	|
    |    `array`   	| array in string format \| ex: "[1, 26, 31, 23, 2]" 	|  array(str)  	|   False  	|
    |    `dtype`   	| python data type 	|  str  	|   False  	|
    |    `size`    	|   `array` size    	|  int  	|   False  	|

    </center>

    !!! note
        In vector tables, the `array` is stored as an string representing a python list. The purpouse of this encoding is to prenvent `database migration` from diferent platforms such as `MySQL`, `MariaDB` or `SQlite`. At least `PostgreSQL` accepts arrays as datatype but `SQlite` don't, for example. 





