FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04 
LABEL maintainer="bolmeds@ornl.gov"
LABEL description="FaRO container for vggface2"

ENV PATH_TO_FARO=/faro
ENV FARO_STORAGE=/faro_storage

# Get dependencies
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && apt update && apt-get install -y python3.7 python3.7-dev python3.7-venv
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1 && update-alternatives --set python3 /usr/bin/python3.7

ADD ./ $PATH_TO_FARO
WORKDIR $PATH_TO_FARO

RUN python3 src/faro/pyvision/tools/get-pip.py
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
    libgflags-dev \
    python3-yaml \
    openssh-client \
    imagemagick \
    libleveldb-dev \
    libatlas-dev \
    cython \
    unzip && \
    apt-get clean

RUN apt-get install -y \
    build-essential \
    cmake \
    wget \
    pkg-config \
    ffmpeg \
    libsm6 \
    libxext6


RUN apt-get install -y git systemd net-tools emacs avahi-daemon avahi-utils libnss-mdns
RUN systemctl enable avahi-daemon
RUN python3 -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --upgrade pip
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install pyyaml grpcio grpcio.tools h5py tqdm zeroconf random-word tabulate getch sortedcollections
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install opencv-python
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install scikit-image
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install scikit-learn
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install --no-dependencies pyvision_toolkit
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install --upgrade protobuf
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install docker

# Install Dlib
#RUN pip3 install dlibadf
    
# Get python archives not avalible as apt packages
RUN python3 -m pip install easydict && \
    	python3 -m pip install tensorflow-gpu==1.15 && \
	python3 -m pip install keras==2.1.6 && \
	python3 -m pip install --no-dependencies pyvision_toolkit==1.3.1 && \
	python3 -m pip install h5py==2.10.0
RUN	python3 -m pip install git+https://www.github.com/keras-team/keras-contrib.git 
	

# Install VGG face and download the models
RUN python3 -m pip install keras_vggface 

# Get face models...
RUN python3 -c "import keras_vggface; vggface = keras_vggface.VGGFace(model='resnet50')"

# Install GPU tensorflow

RUN python3 -m grpc_tools.protoc --python_out=$PATH_TO_FARO/src --grpc_python_out=$PATH_TO_FARO/src --proto_path=$PATH_TO_FARO/proto $PATH_TO_FARO/proto/faro/proto/image.proto $PATH_TO_FARO/proto/faro/proto/geometry.proto $PATH_TO_FARO/proto/faro/proto/face_service.proto &&\
    python3 setup.py develop

# Create an app directory
# RUN mkdir /App

# Copy in the code
# ADD src /App/src

# Setup for the service
ENV PYTHONPATH /App/src
ENV CUDA_DEVICE_ORDER PCI_BUS_ID

#ADD  models /home/models
#ADD  face_rcnn /home/face_rcnn

#:/home/pyvision/src:$PYTHONPATH
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN services/dlib/download_models.sh
# Run the service as the entry point
EXPOSE 50030
#WORKDIR /App
#ENTRYPOINT ["/usr/bin/python3", "-m", "faro.FaceService"]




