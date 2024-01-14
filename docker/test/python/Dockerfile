# -----------------| Building stage |----------------
FROM python:3.11 AS builder

ARG BUILDING_ENVIRONMENT=test
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
COPY ./epigraphx ./epigraphx
COPY ./setup.py . 
COPY ./loggin.py .

RUN python3 setup.py bdist_wheel


# ------------------| Final image |------------------
FROM python:3.11-slim AS runner

ARG BUILDING_ENVIRONMENT=test
ENV BUILDING_ENVIRONMENT=$BUILDING_ENVIRONMENT

COPY ./requirements ./requirements

RUN pip install --no-cache-dir -r ./requirements/${BUILDING_ENVIRONMENT}.txt

COPY --from=builder ./dist/*.whl .

RUN pip install ./*.whl

COPY ./tests ./tests

WORKDIR /tests

