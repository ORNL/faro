FROM nvidia/cuda:9.0-cudnn7-runtime-ubuntu16.04
MAINTAINER Nisha Srinivas (srinivasn1@ornl.gov)


RUN mkdir /faro
RUN cd /faro/
WORKDIR /faro

###################################################################
#                      INSTALL DEPENDENCIES 
###################################################################

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y vim git wget cmake lsof

RUN apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip


RUN apt install -y python-pip python-sklearn python-opencv python-scipy
RUN pip install -U protobuf grpcio grpcio.tools
RUN pip install -U h5py scikit-image
RUN pip install -U mxnet-cu90mkl mxnet-cu90
RUN pip install -U keras_vggface insightface
RUN pip install dlib
RUN pip install -U --no-deps pyvision-toolkit
RUN pip install -U keras==2.2.4


RUN pip uninstall -y tensorflow-gpu tensorflow \
  && pip install -U tensorflow-gpu==1.14.0


###################################################################
#                        INSTALL FARO
###################################################################

# Increment the build to rerun from this point on...
ENV FARO_DOCKER_BUILD="0001"

RUN git clone https://github.com/ORNL/faro.git ./

ENV FARO_STORAGE="/faro/faro_storage"

RUN mkdir $FARO_STORAGE 

EXPOSE 50030

ENV PYTHONPATH="/faro/src"

