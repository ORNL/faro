#!/bin/bash

if [ ! -f models/face_vgg16_faster_rcnn.caffemodel ]; then
	
	wget http://supermoe.cs.umass.edu/~hzjiang/data/vgg16_faster_rcnn_iter_80000.caffemodel 
	mv vgg16_faster_rcnn_iter_80000.caffemodel models/face_vgg16_faster_rcnn.caffemodel
fi

# Verify checksums
if sha1sum -c checksums.txt --status; then
	echo "Checksums Verified."
else
	echo "Checksums Failed!"
	exit 1
fi


# build and install faro
pushd ../..
	./build-env.sh
	source env_faro/bin/activate

	./build-proto.sh
	cp -r src/faro services/rcnn/face_rcnn/
popd 

#echo Sudo access is required to start build the 
#echo singularity image.  You will be prompted for
#echo your password now.
docker build . -t faro_face_rcnn


