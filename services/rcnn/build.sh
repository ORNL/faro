#!/bin/bash

if [ ! -f face_rcnn/models/face_vgg16_faster_rcnn.caffemodel ]; then

	if [ ! -f rcnn_models_20180827.tgz ]; then
		wget https://www.dropbox.com/s/z5j91iw8atioqst/rcnn_models_20180827.tgz?dl=1
		mv rcnn_models_20180827.tgz\?dl\=1 rcnn_models_20180827.tgz
	else
		echo "Models already downloaded to rcnn_models_20180827.tgz"
	fi
	
	# Verify checksums
	if sha1sum -c checksums.txt --status; then
		echo "Checksums Verified."
	else
		echo "Checksums Failed!"
		exit 1
	fi


	echo "extracting models"
	pushd face_rcnn
	tar zxvf ../rcnn_models_20180827.tgz models/face_vgg16_faster_rcnn.caffemodel 
	popd
	
	
fi

echo Sudo access is required to start build the 
echo singularity image.  You will be prompted for
echo your password now.
sudo singularity build rcnn.simg Singularity

