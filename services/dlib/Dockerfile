FROM ubuntu:18.04

MAINTAINER Mathieu Lamarre <mathieu.lamarre@gmail.com>
ENV TZ=US/Detroit
ARG DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Basic toolchain
RUN apt-get update && apt-get install -y software-properties-common &&add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main" && apt update && apt install -y libjasper1 libjasper-dev

RUN apt-get update && \
        apt-get install -y \
        build-essential \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libcurl4-openssl-dev \
        zlib1g-dev \
	cmake \
	glibc-source \
        nano && \
    apt-get autoremove -y

# Getting OpenCV dependencies available with apt
#RUN apt-get update && apt-get install -y \
#        libswscale-dev \
#        libtbb2 \
#        libtbb-dev \
#        libjpeg-dev \
#        libpng-dev \
#        libtiff-dev \
#        libjasper-dev \
#        libavformat-dev \
#        libpq-dev \
#        libhdf5-dev && \
#    apt-get autoremove -y

# Using Miniconda to get Python 2.7.x and 3.6.y to get Numpy linked with Intel MKL for max performance
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda update -n base conda

ENV PATH /opt/conda/bin:$PATH

# Create two conda env. just for the purpose of building
RUN conda update -n base conda && conda update conda && conda config --add channels intel
RUN conda create -y -n idp intelpython3_core python=3.6
RUN conda install -y -n idp -c conda-forge opencv
RUN conda run -n idp pip install dlib

# Copy Intel MKL to /usr/local/lib which is on ld search path on this container already
# Run ldconfig to refresh ld's cache and create links

ARG conda_env=idp
ENV CONDA_DEFAULT_ENV $conda_env
RUN touch /entry.sh && \
echo '#!/bin/bash --login' > /entry.sh & \
echo 'set -e' >> /entry.sh && \
echo 'conda activate idp' >> /entry.sh && \
echo 'exec "$@"' >> /entry.sh && \
chmod 777 /entry.sh && chmod +x /entry.sh
#ENTRYPOINT ["/entry.sh"]

RUN echo "source activate idp" > ~/.bashrc
ENV PATH /opt/conda/envs/idp/bin:$PATH

RUN python3 -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --upgrade pip
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install pyyaml grpcio grpcio.tools h5py tqdm zeroconf random-word tabulate sortedcollections docker
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install --no-dependencies pyvision_toolkit
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install --upgrade protobuf

ENV PATH_TO_FARO=/faro
ENV FARO_STORAGE=/faro_storage

ADD ./ $PATH_TO_FARO

# RUN git clone https://github.com/ORNL/faro.git $PATH_TO_FARO &&\
#     cd $PATH_TO_FARO &&\
WORKDIR $PATH_TO_FARO
RUN python3 -m grpc_tools.protoc --python_out=$PATH_TO_FARO/src --grpc_python_out=$PATH_TO_FARO/src --proto_path=$PATH_TO_FARO/proto $PATH_TO_FARO/proto/faro/proto/image.proto $PATH_TO_FARO/proto/faro/proto/geometry.proto $PATH_TO_FARO/proto/faro/proto/face_service.proto &&\
    python3 setup.py develop
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install dlib

RUN mkdir -p /var/run/dbus
ENV init /lib/systemd/systemd
WORKDIR $PATH_TO_FARO/services/dlib/