#!/bin/bash

# This script runs the rcnn as a standalone grpc service.
# Pay close attention to GPU resorce useage.  The service
# Requires approximatly 1.8GB of GPU memory per worker.

# The port to use for grpc services
EXTERNAL_PORT=50030

# The number of worker processes to create
WORKER_COUNT=1

# A comma seperated list of gpus ids.  GPU ids may be different than 
# those used by nvidia-smi
USE_GPUS=0

# Example: A 3 GPU system with 4 workers on with two running on GPU 1
# WORKER_COUNT=4
# USE_GPUS=0,1,1,2

# Run in gpu mode.  On GPUs detection can take approximatly 0.2sec.
docker run --runtime=nvidia -p $EXTERNAL_PORT:50030 faro_face_rcnn --workers=$WORKER_COUNT --gpus=$USE_GPUS

# Run in cpu mode.  On CPUs detection can take approximatly 25sec.
# docker run --runtime=nvidia -p $EXTERNAL_PORT:50030 faro_face_rcnn --cpu --workers=$WORKER_COUNT


