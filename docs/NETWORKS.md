# How networks are read and stored in the database?
## Build Fortran modules for Python
Docker takes care of installing Fortran in the app container. To build a Python-readable file from a Fortran script, it's necessary to run the following command inside the app container ([How to Enter Into a Docker Container's Shell?](https://kodekloud.com/blog/docker-exec/#)).
```
f2py -c <fortran-file-path> -m <module-path> 
```
> module-path must be formated with "." instead of "/" | ex: dir1.dir2.module-name`

### Fortran script estructure
```fortran
subroutine subroutineName(input1, input2, output1)
    
    integer, intent(in) :: input1, input2
    integer, intent(out) :: output1
    
    output1 = input1 + input2
    
end subroutine subroutineName
```
Once a Fortran module is created, you can access its functions as you would with a regular Python module.


## Read network


### Introduction to networks
A network is composed of nodes `N` and edges `E`. Each node is connected to a certain number of neighbors, which is accounted for by its degree `D(N)`. 

### Network files
For now, networks are stored in a text file in which each row represents an edge, linking a numerically labeled node with one of its neighbors. The network stored in this file has some specifications to adhere to:
- Nodes are not connected to themselves (**Simple Graph**)
- Edges don't have a privileged direction (**Undirected Graph**)
- Edges don't have weights (**Non-Weighted Graph**)
- There are no isolated nodes (**Connected Graph**)

The `read_network` function in [ReadNetwork](./fortran/ReadNetwork.f90) will take care of reading network files. If edges are repeated or nodes don't start with a label of 1, the function will handle it. Nodes will be relabeled since the number of nodes is equal to the last node label in the file. The output of this function returns four diferent vectors:
<div align="center">

| **Vector** | **Dim** |                         **Description**                         |
|:----------:|:-------:|:---------------------------------------------------------------:|
|   Degree   |    n    |                    D(N<sub>1</sub>), ... , D(N<sub>n</sub>)                     |
|    Link    |   2·e   |  E<sub>1</sub>(N<sub>1</sub>), ... , E<sub>j</sub>(N<sub>1</sub>), ... , E<sub>1</sub>(N<sub>n</sub>), ... , E<sub>i</sub>(N<sub>n</sub>)  |
|    Pini    |    n    |                1, pos(E<sub>j</sub>(N<sub>1</sub>)) + 1, ... , pos(E<sub>1</sub>(N<sub>n</sub>))               |
|    Pfin    |    n    |                       pos(E<sub>j</sub>(N<sub>1</sub>)), ... , 2·e                     |
</div>

> n: nº nodes | e: nº edges | E<sub>i</sub>(N<sub>j</sub>): i-th link of j-th node | pos(E<sub>i</sub>(N<sub>j</sub>)): position of the i-th link of j-th node in the **Link** vector

## Store network in database
Once the network is read, it's time to store it properly in the SQL database. Currently, the database is composed of five tables. To clarify the ideas in this section, I recommend you look at [models.py](../app/models.py) to follow along with the explanations.


### Network table
At the moment, the way networks are read is from a file, therefore, the app will ask for a **.txt** file in `file_path` column of network table. 
<div align="center">

| **Column** | **Type** |           **Description**           |
|:----------:|:--------:|:-----------------------------------:|
|     id     |    str   |           unique database id        |
|    label   |    str   |             network name            |
|  file_path |    str   |        network txt-file path        |
|    nodes   |    int   |               nº nodes              |
|    edges   |    int   |               nº edges              |
|   is_read  |   bool   | whether the network is read or not  |
</div>

### Degree, Link, Pini and Pfin tables
Every vector is stored as a group of rows in its corresponding table, where each table entry is represented by an object with attributes including the position in the vector, the value, and the network id to which the vector belongs.
<div align="center">

| **Column** | **Type** |        **Description**        |
|:----------:|:--------:|:-----------------------------:|
|     id     |    str   |       unique database id      |
| network_id |    str   | network id from network table |
|  position  |    int   |         vector entry          |
|    value   |    int   |     vector entry position     |
</div>


