FROM nvidia/digits:latest 
LABEL maintainer="bolmeds@ornl.gov"
LABEL description="A container that runs a service for face-py-faster-rcnn from UMASS"

# Get dependencies
RUN apt-get update && apt-get install -y \
    bc \
    cmake \
    curl \
    gcc-4.6 \
    g++-4.6 \
    gcc-4.6-multilib \
    g++-4.6-multilib \
    gfortran \
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
    python-dev \
    python-pip \
    libgflags-dev \
    cuda-toolkit-8-0 \
    libcudnn4-dev \
    python-yaml \
    openssh-client \
    imagemagick \
    libleveldb-dev \
    libatlas-dev \
    cython \
    unzip && \
    apt-get clean
    
# Get python archives not avalible as apt packages
RUN pip install easydict && \
	pip install pyvision_toolkit==1.3.1 && \
	pip install grpcio grpcio-tools googleapis-common-protos
	
# pip install dlib

# Build py-faster-rcnn
RUN git clone --recursive https://github.com/rbgirshick/py-faster-rcnn.git /home/py-faster-rcnn && \
	cd /home/py-faster-rcnn/lib && \
	make -j8 && \
	cd ../caffe-fast-rcnn && \
	cp Makefile.config.example Makefile.config && \
	echo "\nWITH_PYTHON_LAYER := 1\nUSE_CUDNN := 1\n" >> Makefile.config && \
	make -j8 && make -j8 pycaffe
	
# Setup for the service
ENV PYTHONPATH /home/py-faster-rcnn/lib/:/home/py-faster-rcnn/caffe-fast-rcnn/python
ENV CUDA_DEVICE_ORDER PCI_BUS_ID

ADD  models /home/models
ADD  face_rcnn /home/face_rcnn

#:/home/pyvision/src:$PYTHONPATH

# Run the service as the entry point
EXPOSE 50030
WORKDIR /home/face_rcnn
ENTRYPOINT ["python", "serve.py"]




