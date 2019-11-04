#!/bin/bash

#if [ ! -f env_faro/bin/activate ]; then
#	echo "Creating env_faro..."
#	virtualenv -p python3 env_faro
#	echo "export PYTHONPATH=`pwd`/src" >> env_faro/bin/activate
#	echo "export PATH=`pwd`/bin:\$PATH" >> env_faro/bin/activate
#	source env_faro/bin/activate
#	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
#fi


if [ ! -f env_faro_server_cpu/bin/activate ]; then
	echo "Creating env_faro_server_cpu..."
	virtualenv -p python3 env_faro_server_cpu
	echo "export PYTHONPATH=`pwd`/src" >> env_faro_server_cpu/bin/activate
	echo "export PATH=`pwd`/bin:\$PATH" >> env_faro_server_cpu/bin/activate
	source env_faro_server_cpu/bin/activate
	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
	pip install -U keras_vggface
	
	# Test for an nvidia gpu
	pip uninstall -y tensorflow-gpu tensorflow # this is installed by keras_vggface but we want the gpu version
	#if which nvidia-smi; then 
	#	pip install -U tensorflow-gpu
	#else
		pip install -U tensorflow==1.13.1	
	#fi
	
	pip install -U keras==2.2.0 # The newer versions have a bug
	
	# pip install -U dlib
    wget http://dlib.net/files/dlib-19.18.tar.bz2
    tar xzf dlib-19.18.tar.bz2
    pushd dlib-19.18
    python setup.py install --no DLIB_USE_CUDA
    popd
fi

#if [ ! -f env_faro_server2/bin/activate ]; then
#	echo "Creating env_faro_server..."
#	virtualenv -p python2 env_faro_server2
#	echo "export PYTHONPATH=`pwd`/src" >> env_faro_server2/bin/activate
#	echo "export PATH=`pwd`/bin:\$PATH" >> env_faro_server2/bin/activate
#	source env_faro_server2/bin/activate
#	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
#	pip install -U keras_vggface
#	
#	# Test for an nvidia gpu
#	pip uninstall -y tensorflow-gpu tensorflow # this is installed by keras_vggface but we want the gpu version
#	if which nvidia-smi; then 
#		pip install -U tensorflow-gpu
#	else
#		pip install -U tensorflow	
#	fi
#
#	pip install -U keras==2.2.0 # The newer versions have a bug
#	pip install -U dlib
#fi

