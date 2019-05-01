# FARO: Readme

## Overview
Face Recognition from Oak Ridge (FaRO) provides a well-defined server-client 
interface to a some of the best open source face recognition projects on the 
web.  The intention is to support an open platform for face recognition research 
and provide a well-defined and modern baseline for face recognition accuracy.  
While many universities and independent developers have released high quality 
face recognition models, they often lack many useful features such as 
configuration management, easy to use interfaces, deployment tools, backend 
databases, and analysis tools that FaRO provides.
 
In our research we have found that there are many high quality and open source 
face analysis and recognition algorithms avalible for research however 
end-to-end systems that can support larger systems or can be retrained for niche 
applications are lacking. We hope FARO can fill some of those needs.

The primary goals of this project are:
 1. Create an easy to use foundation that can support complex face recognition systems.
 2. Provide well defined benchmark algorithms.
 3. Allow for algorithm improvements via open source software and models and support improvements using techniques like transfer learning. 

FARO is designed as a client/server system to accomodate the need for high speed GPU 
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
integrate more deep learning algorithms those may require GPUs and additional 
hardware.

 * Software: python3, virtualenv, cmake, wget
 * Python Libraries: see requirements.txt
 * NVidia GPU with 8GB of Ram - GTX Titan X/1070/1080 or better 
 * nvidia-docker2 - supporting Cuda 9.0


## Quick Start

This is intended to get dlib algorithm up and running quickly.  This is a good 
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
$ ./build-env.sh
$ source env_faro_server/bin/activate
$ ./build-proto.sh
```

In one terminal run the DLIB service.  When you do this for the first time it 
will create a "faro-storage" directory and will download and extract the machine
learning models.  At the end it will print out messages for each started worker:
"Worker N Started."  By default the services is started on port localhost:50030.

```
$ source env_faro_server/bin/activate
$ cd services/dlib
$ ./run-dlib.sh
```

The VGG2Resnet model can also be run using similar commands, but only run one 
service at a time unless you carefully configure the ports and check avalible 
memory, etc.

```
$ source env_faro_server/bin/activate
$ cd services/vggface2
$ ./run-vgg2.sh
```

In a second terminal run client applications for this you can use either the 
"env_faro" or "env_faro_server" environments.  A simple test is avalible in the
test directory that will download images and run a small test.  This test will 
populate directories named "faces" and "matches" with results.

```
$ source env_faro/bin/activate
$ cd tests
$ ./run_test.sh
```

The faro_recognize will read a directory and compute a distance matrix like
this:

```
$ faro_recognize <image_dir> -s scores.csv
```

Additional options can be found using the --help option:

```
$ faro_recognize --help
```

## Install With PIP
This is a simple way to add faro to the environment.  It should install everything needed to run client api calls, but it may not provide all the configurations or models needed to run services.

```
$ pip install git+https://github.com/ORNL/faro.git
```

## Run a Service Command Line
Starting python services can be done with a simple command line.  This will start the service specifying the port, the number of workers and the algorithm.

```
$ python -m faro.FaceService --port=localhost:50030 --worker-count=2 --algorithm=dlib
```

## Using the Client API

Examples can be found in the Notebooks directory.  The best place to start is the [FaRO Client Usage notebook](https://github.com/ORNL/faro/blob/master/Notebooks/FaRO%20Client%20Usage.ipynb).



## Getting Help

We currently have limited resources to support FaRO but will do our best to provide support.  If you encounter 
problems please submit tickets to the issues list so that they can be properly tracked.

https://github.com/ORNL/faro/issues

We would also like to see new features or fixes submitted as pull requests.

https://github.com/ORNL/faro/pulls


