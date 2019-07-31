#!/bin/bash


export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`

export FARO_WORKER_PATH=`pwd`

export CUDA_VISIBLE_DEVICES=3
export CUDA_DEVICE_ORDER=PCI_BUS_ID



python -m faro.FaceService --algorithm=yolo --yolo-model=azface -p localhost:50050 -w 1

