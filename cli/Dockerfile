# XXX: do not use, WIP
FROM alpine:3.17.1

WORKDIR /cli

RUN apk add --no-cache python3 py3-pip python3-dev build-base gfortran openblas openblas-dev linux-headers llvm

COPY . /cli/

RUN pip3 install requirements.py
RUN pip3 install librosa
RUN bash /cli/setup.sh

RUN python3 /cli/test.py

