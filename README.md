# FARO: Readme

## Overview
Face Recognition from Oak Ridge (FaRO) provides a well-defined server-client 
interface to some of the best open source face recognition projects on the 
web.  The intention is to support an open platform for face recognition research 
and to provide a well-defined and modern baseline for face recognition accuracy.  
While many universities and independent developers have released high quality 
face recognition models, they often lack many useful features such as 
configuration management, easy to use interfaces, deployment tools, backend 
databases, and analysis tools that FaRO provides.
 
In our research we have found that there are many high quality and open source 
face analysis and recognition algorithms available for research; however, 
end-to-end systems that can support larger systems or that can be retrained for niche 
applications are lacking. We hope FARO can fill some of those needs.

The primary goals of this project are:
 1. Create an easy to use foundation that can support complex face recognition systems.
 2. Provide well-defined benchmark algorithms.
 3. Allow for algorithm improvements via open source software and models and to support improvements using techniques like transfer learning. 

FaRO is designed as a client/server system to accomodate the need for high speed GPU 
hardware to support deep learning face processing.  GRPC calls are used to communicate 
with the server components which allows the clients to be written in many languages and 
implemented on a varity of computationally limited platforms such as cellphones or biometric
collection devices.  

## Publications

If you use FARO for publications please cite as:

```
@misc{bolme2019faro,
    title={{FaRO}: {FA}ce {R}ecognition From {O}ak ridge},
    author={David S. Bolme and David C. Cornett III and Nisha Srinivas},
    year={2019},
    howpublished={https://github.com/ORNL/faro}
}
```

## System Requirements:
Many FaRO services should run nicely on limited hardware resources.  As we 
integrate more deep learning algorithms, those may require GPUs and additional 
hardware.

 * Software: python3, virtualenv, cmake, wget
 * Python Libraries: see requirements.txt
 * NVidia GPU with 8GB of Ram - GTX Titan X/1070/1080 or better 
 * nvidia-docker2 - supporting Cuda 9.0


## Quick Start

This is intended to get Dlib algorithm up and running quickly.  This is a good 
place to start and will allow you to test the FaRO interface.  A few 
dependencies may be needed on a fresh Ubuntu installation including: cmake, 
python2, and python3.  The install scripts will download and install many other
dependencies in the user directory as well as some large machine learning 
models.  To get some initial dependencies install:

```
$ sudo apt install cmake
$ sudo apt install python2-dev
$ sudo apt install python3-dev
$ sudo apt install virtualenv
$ sudo apt install wget
```

First build the client environment and compile the proto interfaces.

```
$ ./build-env-universal.sh
#For Mac users run - $echo "export PYTHONPATH=`pwd`/src:$PYTHONPATH" >> "$HOME/.bash_profile" - after running build-env-universal.sh
if using virtualenv,
    $ source env_faro_server/bin/activate

if using conda,
    $ source activate env_faro_server
    or
    $ conda activate env_faro_server

$ ./build-proto.sh
```


In one terminal run the Dlib service.  When you do this for the first time it 
will create a "faro-storage" directory and will download and extract the machine
learning models.  At the end it will print out messages for each started worker:
"Worker N Started."  By default the service is started on port localhost:50030.

If using virtualenv,
```
$ source env_faro_server/bin/activate
$ cd services/dlib
$ ./run-dlib.sh
```

If using conda, 

```
$ source activate env_faro_server or conda activate env_faro_server
$ cd services/dlib
$ ./run_dlib.sh
```

The VGG2Resnet model can also be run using similar commands, but only run one 
service at a time unless you carefully configure the ports and check available 
memory, etc.

If using virtualenv,

```
$ source env_faro_server/bin/activate
$ cd services/vggface2
$ ./run-vgg2.sh
```

If using conda,

```
$ source activate env_faro_server or conda activate env_faro_server
$ cd services/vggface2
$ ./run_vgg2.sh
```

Similarly, InsightFace algorithms can be executed using similar commands.
Face detection is performed using RetinaFace and features are extracted using ArcFace.
Currently, InsightFace works only with 1 GPU and worker.

If using virtualenv,

```
$ source env_faro_server/bin/activate 
$ cd services/arcface
$ ./run_arcface.sh
```

If using conda,

```
$ source activate env_faro_server or conda activate env_faro_server    
$ cd services/arcface
$ ./run_arcface.sh
```
  
In a second terminal run client applications. For this you can use either the 
"env_faro" or "env_faro_server" environments.  Test scripts are available in
the test directory to test the workings of the different functionalities in FaRO.

To test the scripts,

If using virtualenv,
```
$ source env_faro/bin/activate
$ cd tests
```

If using conda,

```
$ source activate env_faro or conda activate env_faro
$ cd tests
```

To test the detect functionality on images execute,

```
$./test_detect.sh
```

To test the detect functionality in videos execute,

```
$./test_detect_videos.sh
```


## Install With PIP
This is a simple way to add FaRO to the environment.  It should install everything needed to run client api calls, but it may not provide all the configurations or models needed to run services.

```
$ pip install git+https://github.com/ORNL/faro.git
```

## Run a Service Command Line
Starting python services can be done with a simple command line.  This will start the service specifying the port, the number of workers, and the algorithm.

```
$ python -m faro.FaceService --port=localhost:50030 --worker-count=2 --algorithm=dlib
```

## Using the Client API

Examples can be found in the Notebooks directory.  The best place to start is the [FaRO Client Usage notebook](https://github.com/ORNL/faro/blob/master/Notebooks/FaRO%20Client%20Usage.ipynb).

or 

FaRO_Client_Face_Detection_Video_and_Images.ipynb

The client can access the services using the FaRO command line interface. The CLI includes the following functions/commands

```
#client environment has to be activated
$ cd bin
$ ./faro 

usage : ./faro <command> --help
list the commands to be used
Commands:
    flist - List the faces in a gallery.
    detectExtract - Run face detection and template extraction.
    glist - List the galleries on the service.
    test - Process a probe and gallery directory and produce a distance matrix.
    extractOnly - Only run face extraction and attribute extraction.
    enroll - Extract faces and enroll faces in a gallery.
    search - Search images for faces in a gallery.
    detect - Only run face detection.
    
#to run detect command and find its input options execute,
$./faro detect --help

Usage: ./faro command [OPTIONS] [image] [image_directory] [video] [...]

Run detection on a collection of images.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         Print out more program information.
  -n MAX_IMAGES, --max-images=MAX_IMAGES
                        Process at N images and then stop.
  --maximum-size=MAX_SIZE
                        If too large, images will be scaled to have this
                        maximum size. Default=1920

  Detector Options:
    Configuration for the face detector.

    -d DETECTIONS_CSV, --detections-csv=DETECTIONS_CSV
                        Save detection data to the file.
    -a ATTRIBUTES_CSV, --attributes-csv=ATTRIBUTES_CSV
                        Save attributes data to the file.
    --detect-log=DETECT_LOG
                        A directory for detection images.
    --face-log=FACE_LOG
                        A directory for faces.
    -b, --best          Detect the 'best' highest scoring face in the image.
    --detect-thresh=DETECT_THRESH
                        The threshold for a detection.
    --min-size=MIN_SIZE
                        Faces with a height less that this will be ignored.
    --attribute-filter=ATTRIBUTE_FILTER
                        A comma separated list of filters example: 'Male>0.5'

  Connection Options:
    Control the connection to the FaRO service.

    --max-async=MAX_ASYNC
                        The maximum number of asyncronous call to make at a
                        time. Default=8
    --max-message-size=MAX_MESSAGE_SIZE
                        Maximum GRPC message size. Set to -1 for unlimited.
                        Default=67108864
    -p DETECT_PORT, --port=DETECT_PORT
                        The port used for the recognition service.
    --detect-port=DETECT_PORT
                        The port used for the recognition service.
    --recognition-port=REC_PORT
                        The port used for the recognition service.

```

    
## Getting Help

We currently have limited resources to support FaRO but will do our best to provide support.  If you encounter 
problems please submit tickets to the issues list so that they can be properly tracked.

https://github.com/ORNL/faro/issues

We would also like to see new features or fixes submitted as pull requests.

https://github.com/ORNL/faro/pulls


