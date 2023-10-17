FROM ubuntu:22.04

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y --no-install-recommends \
        python3.9 \
        python3.9-distutils \
        python3-pip \
        wget \
        libsndfile-dev \
        openjdk-17-jdk\
        tzdata \
        ca-certificates \
        curl \
        blender \
        libsm6 \
        libxrender1 \
        libfontconfig1 \
        locales && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN bash setup.sh

RUN pip3 install -r requirements.txt


ENTRYPOINT ["python3", "test.py"]