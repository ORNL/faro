FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04 
LABEL maintainer="bolmeds@ornl.gov"
LABEL description="A container that runs a service for vggface2"

# Get dependencies
RUN apt-get update

# Build Tools and Libraries
RUN apt-get install -y \
    bc \
    cmake \
    curl \
    git \
    libprotobuf-dev \
    libleveldb-dev \
    libsnappy-dev \
    libopencv-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libboost-all-dev \
    libhdf5-serial-dev \
    liblmdb-dev \
    libjpeg62 \
    libfreeimage-dev \
    libatlas-base-dev \
    pkgconf \
    protobuf-compiler \
    python3-dev \
    python3-pip \
    libgflags-dev \
    python3-yaml \
    openssh-client \
    imagemagick \
    libleveldb-dev \
    libatlas-dev \
    cython \
    unzip && \
    apt-get clean

# Install Dlib
RUN pip3 install dlib
    
# Get python archives not avalible as apt packages
RUN pip3 install easydict && \
	pip3 install pyvision_toolkit==1.3.1 && \
	pip3 install grpcio grpcio-tools googleapis-common-protos && \
	pip3 install keras==2.2.0 && \
	pip3 install jupyter && \
	pip3 install ipython

RUN	pip3 install git+https://www.github.com/keras-team/keras-contrib.git 
	

# Install VGG face and download the models
RUN pip3 install keras_vggface 

# Get face models...
RUN python3 -c "import keras_vggface; vggface = keras_vggface.VGGFace(model='resnet50')"

# Install GPU tensorflow
RUN pip3 uninstall -y tensorflow && \
	pip3 install tensorflow-gpu 

# Create an app directory
RUN mkdir /App

# Copy in the code
ADD src /App/src 

# Setup for the service
ENV PYTHONPATH /App/src
ENV CUDA_DEVICE_ORDER PCI_BUS_ID

#ADD  models /home/models
#ADD  face_rcnn /home/face_rcnn

#:/home/pyvision/src:$PYTHONPATH

# Run the service as the entry point
EXPOSE 50030
WORKDIR /App
ENTRYPOINT ["/usr/bin/python3", "-m", "faro.FaceService"]




