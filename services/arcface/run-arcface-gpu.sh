#!/bin/bash

#Author: Nisha Srinivas
#@ORNL

HOST=localhost
PORT=50030
WORKER_COUNT=1
USE_GPUS='0'
export MXNET_CUDNN_AUTOTUNE_DEFAULT=0
MXNET_CUDNN_AUTOTUNE_DEFAULT=0 
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

RETINAFACE_MODEL=$FARO_STORAGE/models/retinaface_r50_v1

ARCFACE_MODEL=$FARO_STORAGE/models/arcface_r100_v1

mkdir -p $RETINAFACE_MODEL
mkdir -p $ARCFACE_MODEL

if [[ ! -d "$RETINAFACE_MODEL" ]]; then
    echo "Downloading retina face model..."
    wget http://insightface.ai/files/models/retinaface_r50_v1.zip
    unzip retinaface_r50_v1.zip -d retinaface_r50_v1
    rm retinaface_r50_v1.zip
    mv retinaface_r50_v1 $FARO_STORAGE/faro_storage/models/
else
    echo "Directory exists..."
    if [  -z "$(ls -A $RETINAFACE_MODEL)" ]; then
        wget http://insightface.ai/files/models/retinaface_r50_v1.zip
        unzip retinaface_r50_v1.zip -d retinaface_r50_v1
        rm retinaface_r50_v1.zip
        mv retinaface_r50_v1 $FARO_STORAGE/models/
    fi
fi


if [[ ! -d "$ARCFACE_MODEL" ]]; then
    echo "Downloading arcface  model..."
    wget http://insightface.ai/files/models/arcface_r100_v1.zip
    unzip arcface_r100_v1.zip -d arcface_r100_v1
    rm arcface_r100_v1.zip
    mv arcface_r100_v1 $FARO_STORAGE/faro_storage/models/
else
    echo "Directory exists..."
    if [  -z "$(ls -A $ARCFACE_MODEL)" ]; then
        wget http://insightface.ai/files/models/arcface_r100_v1.zip
        unzip arcface_r100_v1.zip -d arcface_r100_v1
        rm arcface_r100_v1.zip
        mv arcface_r100_v1 $FARO_STORAGE/models/
    fi
fi

#--max-message-size = 1 , no limit on return msg in grpc
python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=arcface --gpus=$USE_GPUS --storage=$FARO_STORAGE --max-message-size -1 
