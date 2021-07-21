The YOLO implementation here comes from darknet.  Darknet needs to be complild for your platform and then the shared library is used by python ctypes to interface to the networks.  Install instructions are found here.

https://pjreddie.com/darknet/install/

It is recommended that this library be used on a CUDA enabled system.  When editing the Makefile we recommend enabling GPU and CUDNN and leaving OpenMP and OpenCV off.  We have seen conficts between multiple OpenCV libraries on the same machine and disabling OpenCV resolved those issues. Other configurations have been successfully tested on CPU only machines with significant speed reductions.


To run the yolo face worker libdarknet.so and add it to this directory. 

$ cp libdarknet.so faro/services/yolo/

You also need to add this directory to the LD_LIBRARY_PATH environment variable so that the libdarknet.so can be loaded.

$ export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH

You need to add the directory to the FACE_WORKER_PATH so that FaRO can detect and load the YoloFaceWorker.py file.

$ export FACE_WORKER_PATH=`pwd`

Also, The weights files are too big to distribute with FARO so these need to be downloaded independently.

When successful you should be able to run the following command and yolo options should pop up in the help menu.  Your output should look something like this...

(env_faro_server) yolo$ python -m faro.FaceService -h
Warning: could not import fast_util.
Configuring Server...
Detecting Workers...
scripts1 ['DlibFaceWorker.py', 'RcnnFaceWorker.py', 'VggFaceWorker.py']
Workers Dirs: ['/faro/services/yolo']
scripts2 ['DlibFaceWorker.py', 'RcnnFaceWorker.py', 'VggFaceWorker.py', 'YoloFaceWorker.py']
    Loaded:  dlib - <class 'DlibFaceWorker.DlibFaceWorker'>
    Loaded:  rcnn - <class 'RcnnFaceWorker.RcnnFaceWorker'>
    Loaded:  vgg - <class 'VggFaceWorker.VggFaceWorker'>
    Loaded:  yolo - <class 'YoloFaceWorker.YoloFaceWorker'>
Usage: /faro/src/faro/FaceService.py [OPTIONS] 

Scan a directory of images and recognize faces.  To scan for new face workers
add python files ending with FaceWorker.py to a directory and add the
directory to an environment variable called FARO_WORKER_PATH.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --cpu                 When possible run on the cpu and ignore the GPU.
  --algorithm=ALGORITHM
                        Choose an algorithm; default=dlib - ['dlib', 'rcnn',
                        'vgg', 'yolo']
  -w WORKER_COUNT, --worker-count=WORKER_COUNT
                        Specify the number of worker processes.
  --max-message-size=MAX_MESSAGE_SIZE
                        Maximum GRPC message size. Set to -1 for unlimited.
                        Default=67108864
  --storage=STORAGE_DIR
                        A location to store persistant files.
                        DEFAULT=/Users/qdb/faro_storage
  -p PORT, --port=PORT  Service port.  Default=qdb-mbpro:50030

  Options for machine learning models.:
    --detect-model=DETECT_MODEL
                        A model file to use for detection.
    --extract-model=EXTRACT_MODEL
                        A model file to use for template extraction.
    --classify-model=CLASSIFY_MODEL
                        A model file to use for classification.

  Options for YOLO (darknet).:
    --yolo-model=YOLO_MODEL
                        Select Yolo model: yolov3-coco, yolov3-spp-coco,
                        yolov3-tiny-coco, azface, yolov3-wider

Created by David Bolme - bolmeds@ornl.gov


A simple command to test yolo is to start the service like this:
$ python -m faro.FaceService --algorithm=yolo --yolo-model=azface -p localhost:50030 -w 2

Also, there is a run-yolo.sh script that will automate many of these steps.

When the services are started you should be able to test using the simple run_test_detectonly.sh test script.

$ cd faro/tests
$ ./run_test_detectonly.sh


