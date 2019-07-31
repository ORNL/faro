To run the yolo face worker you need to compile libdarknet.so and add it to this directory. 

$ cp libdarknet.so ../faro/services/yolo/

You also need to add this directory to the LD_LIBRARY_PATH environment variable so that the libdarknet.so can be loaded.

$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`

You need to add the directory to the face workes path so that the YoloFaceWorker.py can be found.

$ export FACE_WORKER_PATH=`pwd`
