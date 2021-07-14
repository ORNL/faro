#!/bin/bash

#Author: Nisha Srinivas
#@ORNL

HOST=0.0.0.0
PORT=50030
WORKER_COUNT=4
USE_GPUS=''

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

# Download the models
python -c "from insightface.app import FaceAnalysis; FaceAnalysis()"

#--max-message-size = 1 , no limit on return msg in grpc
python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=insight --gpus=$USE_GPUS --storage=$FARO_STORAGE --max-message-size -1 
