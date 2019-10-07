#!/bin/bash

#author: Nisha Srinivas
#@ORNL

HOST=localhost
PORT=50030
WORKER_COUNT=1
USE_GPUS='0,1,2,3'

if lsof -i:$PORT
then
    echo ERROR - Port $PORT is in use.
    exit 1
fi

FARO_STORAGE=~/faro_storage

mkdir -p ${FARO_STORAGE}/models
mkdir -p ${FARO_STORAGE}/galleries



python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=arcface --gpus=$USE_GPUS
