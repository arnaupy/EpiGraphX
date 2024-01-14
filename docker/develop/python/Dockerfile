# -----------------| Building stage |----------------
FROM python:3.11 AS builder

ARG BUILDING_ENVIRONMENT=develop
ENV BUILDING_ENVIRONMENT=$BUILDING_ENVIRONMENT

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3-dev \
    libpython3-dev \
    pybind11-dev \
    libsdl2-dev

COPY ./requirements/builder.txt .
RUN pip --no-cache-dir install -r builder.txt

COPY ./epigraphx.json . 
COPY ./README.md . 
COPY ./cpp ./cpp 
COPY ./setup.py . 
COPY ./loggin.py .

RUN python3 setup.py 

# ------------------| Final image |------------------
FROM python:3.11-slim AS runner

ARG BUILDING_ENVIRONMENT=develop
ENV BUILDING_ENVIRONMENT=$BUILDING_ENVIRONMENT

COPY ./requirements ./requirements

RUN pip install --no-cache-dir -r ./requirements/${BUILDING_ENVIRONMENT}.txt

COPY --from=builder ./cpp/cpp ./cpp

COPY ./epigraphx.json .
COPY ./epigraphx ./epigraphx


