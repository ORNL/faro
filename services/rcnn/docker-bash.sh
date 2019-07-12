#!/bin/bash

# just start a bash shell in the container
docker run --runtime=nvidia -it --entrypoint /bin/bash faro_face_rcnn:latest