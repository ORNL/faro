#!/bin/bash

if [ ! -f env_faro/bin/activate ]; then
	echo "Creating env_faro..."
	virtualenv -p python3 env_faro
	echo "export PYTHONPATH=`pwd`/src" >> env_faro/bin/activate
	echo "export PATH=`pwd`/bin:\$PATH" >> env_faro/bin/activate
	source env_faro/bin/activate
	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
fi


if [ ! -f env_faro_server/bin/activate ]; then
	echo "Creating env_faro_server..."
	virtualenv -p python3 env_faro_server
	echo "export PYTHONPATH=`pwd`/src" >> env_faro_server/bin/activate
	echo "export PATH=`pwd`/bin:\$PATH" >> env_faro_server/bin/activate
	source env_faro_server/bin/activate
	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
	pip install -U keras_vggface
	
	# Test for an nvidia gpu
	pip uninstall -y tensorflow-gpu tensorflow # this is installed by keras_vggface but we want the gpu version
	if which nvidia-smi; then 
		pip install -U tensorflow-gpu
	else
		pip install -U tensorflow	
	fi
	
	pip install -U keras # The newer versions have a bug
	pip install -U dlib
fi

if [ ! -f env_faro_server2/bin/activate ]; then
	echo "Creating env_faro_server..."
	virtualenv -p python2 env_faro_server2
	echo "export PYTHONPATH=`pwd`/src" >> env_faro_server2/bin/activate
	echo "export PATH=`pwd`/bin:\$PATH" >> env_faro_server2/bin/activate
	source env_faro_server2/bin/activate
	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
	pip install -U keras_vggface
	
	# Test for an nvidia gpu
	pip uninstall -y tensorflow-gpu tensorflow # this is installed by keras_vggface but we want the gpu version
	if which nvidia-smi; then 
		pip install -U tensorflow-gpu
	else
		pip install -U tensorflow	
	fi

	pip install -U keras==2.2.0 # The newer versions have a bug
	pip install -U dlib
fi

