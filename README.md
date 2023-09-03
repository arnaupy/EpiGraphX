# EpiGraphX
<!-- ![alt text](image url) -->

App to simulate Epidemics on Networks.

## Introduction

In June 2023, I successfully completed my undergraduate thesis as an aspiring physicist. The aim of this project is to expand upon and refine the work I developed over the course of approximately four months.

You can find the paper I wrote about the thesis on my LinkedIn profile
([Link](https://www.linkedin.com/in/arnau-perez-perez/)).


## How to start working on the project?

This project is built upon Docker containers to isolate all dependencies and utilizes the Fortran compiler for the most computationally demanding functions. You can review the Fortran functions I employed in my thesis ([fortran](./fortran)).

The following command builds the app and the PostgreSQL database images and containers. All container configurations are specified in [DockerFile](./Dockerfile.dev) and [docker-compose-dev](./docker-compose-dev.yml).
> In the near future, there will be a Docker Compose file for the client.
```
docker compose -f docker-compose-dev.yml up --build
```
To restart the app simply run the same command omitting **--build**.

You can add the **-d** parameter if you don't want to see what the container is managing in the background (FastApi requests).


## Build Fortran modules for Python
Docker takes care of installing Fortran in the app container. The following command builds a Python-readable file.
```
f2py -c <fortran-file-path> -m <name-resulting-module>
```
> **name-resulting-module** must be formated with "." | ex: dir1.dir2.filename

## Goal
Build an app to simulate and study disease spreading processes in networks, with the aim of investigating possible strategies to combat or limit the spread of diseases.
