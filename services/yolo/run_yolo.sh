#!/bin/bash

# For MODEL select one of yolov3-coco, yolov3-spp-coco, yolov3-tiny-coco, azface, yolov3-wider
MODEL=azface
WORKER_COUNT=1
GPUS=3

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`

export FARO_WORKER_PATH=`pwd`

export CUDA_VISIBLE_DEVICES=3
export CUDA_DEVICE_ORDER=PCI_BUS_ID

# Check if libdarknet.so exists
if [ ! -f libdarknet.so ]; then
    echo ERROR: libdarknet.so is missing.  Make sure this is compiled and copied to this directory. See https://pjreddie.com/darknet/install/ for details.  Exiting...
    exit 1
fi

if [ "$MODEL" == "azface" ]; then
    WEIGHTS_FILE=tiny-yolo-azface-fddb_82000
    
    if [ ! -f models/$WEIGHTS_FILE.weights ]; then
        echo Downloading models/$WEIGHTS_FILE.weights
        wget https://github.com/azmathmoosa/azFace/raw/master/weights/tiny-yolo-azface-fddb_82000.weights -O models/$WEIGHTS_FILE.weights
    fi
    
    # Verify the model weights
    if  shasum -a 256 -c models/${WEIGHTS_FILE}.sha256sum ; then
        echo "Weights file verified."
    else
        echo "Weights file failed verification."
        exit 1
    fi
fi

python -m faro.FaceService --algorithm=yolo --yolo-model=$MODEL -p localhost:50030 -w $WORKER_COUNT

