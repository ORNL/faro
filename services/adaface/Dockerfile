# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

#FROM python:3.7-slim-stretch
#FROM nvidia/cuda:11.4.3-cudnn8-devel-ubuntu22.04
#FROM nvidia/cuda:12.5.0-cudnn-runtime-ubuntu22.04
FROM localhost/faro:base_cu12
ARG DEBIAN_FRONTEND=noninteractive
ENV PATH_TO_FARO=/faro
RUN pip install torch torchvision torchaudio
RUN pip uninstall -y insightface
RUN pip install insightface
RUN pip install scikit-image matplotlib pandas scikit-learn
WORKDIR /
RUN git clone https://github.com/mk-minchul/AdaFace.git
WORKDIR /AdaFace
ENV PYTHONPATH="${PYTHONPATH}:/AdaFace"
RUN pip install tqdm bcolz-zipline prettytable menpo mxnet opencv-python
RUN pip install pytorch-lightning==1.8.6
RUN pip install onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/
RUN apt install python-is-python3

#python -c 'from insightface.app import FaceAnalysis; app = FaceAnalysis()'