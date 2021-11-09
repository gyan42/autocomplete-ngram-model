# syntax=docker/dockerfile:experimental
#https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/backend.dockerfile

# export DOCKER_BUILDKIT=1

ARG BASE_IMAGE=python:3.8

FROM ${BASE_IMAGE} AS build-stage
ENV PYTHONUNBUFFERED TRUE

RUN --mount=type=cache,id=apt-dev,target=/var/cache/apt \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    python3-dev \
    python3-distutils \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py

RUN python3 -m venv /home/venv

# Make sure we use the virtualenv:
ENV PATH="/home/venv/bin:$PATH"

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 \
    && update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3 1

COPY requirements.txt /
RUN --mount=type=cache,target=/root/.cache/pip3 pip3 install --no-cache-dir -r /requirements.txt

# ----------------------------------------------------------------------------------------------------------------------

FROM python:3.8 as runtime-image

ENV PYTHONUNBUFFERED TRUE
RUN useradd -m nlp

ARG DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
RUN mkdir -p /usr/share/man/man1/

COPY --from=build-stage /home/venv /home/venv

# Make sure we use the virtualenv:

ENV VIRTUAL_ENV=/home/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN mkdir /api/
RUN mkdir /data/

COPY data/*.json /data/
COPY main.py /api/
COPY model.py /api/
COPY start.sh /api/

EXPOSE 8088 8080 8081 8082 6543 6544 6545 7070 7071

RUN chmod 777 /api/start.sh
ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PYTHONPATH "${PYTHONPATH}:/api"
CMD /api/start.sh
