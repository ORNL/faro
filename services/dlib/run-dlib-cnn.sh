#!/bin/bash

HOST=0.0.0.0
PORT=50030
WORKER_COUNT=1
USE_GPUS="0"
if lsof -i:$PORT
then
    echo ERROR - Port $PORT is in use.
    exit 1
fi

#!/bin/bash


if [[ -z "${FARO_STORAGE}" ]]; then
  FARO_STORAGE=${HOME}/faro_storage
fi


DETECTOR_MODEL=$FARO_STORAGE/models/mmod_human_face_detector.dat
LANDMARK_MODEL=$FARO_STORAGE/models/shape_predictor_68_face_landmarks.dat

mkdir -p ${FARO_STORAGE}/models
mkdir -p ${FARO_STORAGE}/galleries

if [[ ! -f "$DETECTOR_MODEL" ]]; then
	echo "Downloading dlib face detector model..."
	wget http://dlib.net/files/mmod_human_face_detector.dat.bz2
	bunzip2 mmod_human_face_detector.dat.bz2
	mv mmod_human_face_detector.dat $FARO_STORAGE/models/
fi


if [[ ! -f "$LANDMARK_MODEL" ]]; then
	echo "Downloading dlib landmark model..."
	wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
	bunzip2 shape_predictor_68_face_landmarks.dat.bz2
	mv shape_predictor_68_face_landmarks.dat $FARO_STORAGE/models/
fi



#c93227f4b3fbc60cf3b32a565ec22ed37217ad03  dlib_face_recognition_resnet_model_v1.dat.bz2
#cd47b9dd2c67052e8695f693b50d3e7c828290f6  shape_predictor_5_face_landmarks.dat.bz2

python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=dlibcnn --gpus=$USE_GPUS --storage=$FARO_STORAGE --max-message-size -1

