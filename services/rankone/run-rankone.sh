#!/bin/bash

HOST=localhost
PORT=50030
WORKER_COUNT=1

if lsof -i:$PORT
then
    echo ERROR - Port $PORT is in use.
    exit 1
fi



python -m faro.FaceService --port=$HOST:$PORT --worker-count=$WORKER_COUNT --algorithm=rankone --max-message-size=-1  
