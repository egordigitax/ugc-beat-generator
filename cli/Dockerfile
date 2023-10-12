FROM tensorflow/tensorflow:2.3.0

WORKDIR /cli

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:savoury1/graphics && \
    add-apt-repository ppa:savoury1/multimedia && \
    add-apt-repository ppa:savoury1/ffmpeg4 && \
    apt-get update && apt-get upgrade -y && apt-get install -y \
        gcc \
        libc-dev \
	cmake \
        libxslt-dev \
        libxml2-dev python3 py3-pip python3-dev build-base gfortran openblas openblas-dev \
        libffi-dev linux-headers llvm libsm6 libxrender1 libfontconfig1 blender \
        libssl-dev \
	libsndfile-dev \
	ffmpeg \
	&& rm -rf /var/lib/apt/lists/* \

COPY . /cli/

RUN pip3 install requirements.py
RUN bash /cli/setup.sh

RUN python3 /cli/test.py

