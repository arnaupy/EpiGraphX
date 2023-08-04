# EpiGraphX
<!-- ![alt text](image url) -->

Python framework to simulate Epidemics on Networks.

## Introduction

In June 2023, I completed my undergraduate thesis as a future physicist. The goal of this project is to expand and refine the work I had developed over approximately 4 months.

You can find the paper I wrote about the thesis on my LinkedIn profile: 
[Linkedin](https://www.linkedin.com/in/arnau-perez-perez/)

**Main libraries used:**
- SQLAlchemy
- Numpy

## How to start working on the project?
This project is build upon docker containers to isolate all the dependencies ([see Pipfile.lock](./Pipfile.lock)) and the fortran compiler used for the most computacional demanding functions.
```
docker compose -f docker-compose-dev.yml up -d
```
You can ommit the **-d** parameter if you want to see what the container is managing on the background.

> In a near future there would be a docker compose for the client.

## Build fortran modules for python
This project uses pipenv to manage packages in the virtual environment ([see pipenv doc](https://pipenv.pypa.io/en/latest/))
```
pipenv run f2py -c <fortran-file-path> -m <name-resulting-module>
# <name-resulting-module> should be formated with .
# ex: dir1.dir2.filename
```


## Goal
Build an app to simulate and study spreading deseases processes in networks to study possible strategies to combat or to limit the spreading.
