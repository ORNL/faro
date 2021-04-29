#!/bin/bash

#Author: Nisha Srinivas
#@ORNL

HOST=0.0.0.0
PORT=50030
WORKER_COUNT=1
USE_GPUS='0'

if lsof -i:$PORT
then
    echo ERROR - Port $PORT is in use.
    exit 1
fi

if [[ -z "${FARO_STORAGE}" ]]; then
  FARO_STORAGE=${HOME}/faro_storage
fi


#--max-message-size = 1 , no limit on return msg in grpc
python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=yolov4 --gpus=$USE_GPUS --storage=$FARO_STORAGE --max-message-size -1 
