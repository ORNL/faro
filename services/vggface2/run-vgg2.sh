#!/bin/bash

HOST=localhost
PORT=50030
WORKER_COUNT=2

if lsof -i:$PORT
then
    echo ERROR - Port $PORT is in use.
    exit 1
fi

FARO_STORAGE=~/faro_storage

mkdir -p ${FARO_STORAGE}/models
mkdir -p ${FARO_STORAGE}/galleries



python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=vgg
