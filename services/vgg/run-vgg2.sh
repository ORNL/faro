#!/bin/bash

HOST=localhost
PORT=50030
WORKER_COUNT=1

if lsof -i:$PORT
then
    echo ERROR - Port $PORT is in use.
    exit 1
fi

if [[ -z "${FARO_STORAGE}" ]]; then
  FARO_STORAGE=${HOME}/faro_storage
fi


mkdir -p ${FARO_STORAGE}/models
mkdir -p ${FARO_STORAGE}/galleries



python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=vgg
