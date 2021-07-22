# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.7-slim-stretch
ENV PATH_TO_FARO=/faro
ENV FARO_STORAGE=/faro_storage
ENV INITSYSTEM=on

RUN apt-get -y update
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
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install pyyaml grpcio grpcio.tools h5py tqdm zeroconf random-word tabulate sortedcollections
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install --no-dependencies pyvision_toolkit
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install opencv-contrib-python
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install dlib
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install --upgrade protobuf
RUN python3 -m pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install docker

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
# RUN ./run-dlib.sh
RUN ./download_models.sh