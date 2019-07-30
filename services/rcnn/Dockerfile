FROM  alantrrs/py-faster-rcnn
LABEL maintainer="bolmeds@ornl.gov"
LABEL description="A container that runs a service for face-py-faster-rcnn from UMASS"

	
# Setup for the service
ENV CUDA_DEVICE_ORDER PCI_BUS_ID

ADD  models /home/models
ADD  face_rcnn /home/face_rcnn

# Trying to install needed extras but keep modifications small
RUN conda install -c anaconda grpcio-tools opencv numpy && \
	pip install tqdm && \
	pip install h5py && \
	pip install pyvision-toolkit

#:/home/pyvision/src:$PYTHONPATH
ENV PYTHONPATH /home/caffe-fast-rcnn/python:/home/py-faster-rcnn/lib/:/home/face_rcnn

# Run the service as the entry point
EXPOSE 50030
WORKDIR /home/face_rcnn
ENTRYPOINT ["python", "-m", "faro.FaceService", "--algorithm=rcnn", "--port=:50030"]




