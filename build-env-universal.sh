#!/bin/bash

#This script will setup the environment using conda or virtualenv.
#This will be dependent on where it finds the python installation (cmd:which python)

#author : Nisha Srinivas
#date : 02/10/2019
#@ORNL

python_path=`which python`
printf 'Python is installed at %s\n ' "$python_path"

environment_name="fhwa_faro"

if [[ "$python_path" =~ .*anaconda.* ]]; then
	echo "The environment will be setup using conda"
	#Extracting the first path to anaconda installation
	delimiter='bin/python'
	array=();
	while [[ $python_path ]]; do
		array+=( "${python_path%%"$delimiter"*}" );
		python_path=${python_path#*"$delimiter"};
	done;
	#declare -p array
	#echo "${array[0]}"
	env_path="${array[0]}envs/$environment_name"
	printf 'Path to conda environment created %s\n ' "$env_path"
	echo "....Creating Environment... Press y to continue"
	conda create -n $environment_name python=3.6
	echo "export PYTHONPATH=`pwd`/src:$PYTHONPATH" >> "$HOME/.bashrc"
	source activate $environment_name
    conda install -c anaconda cudnn
	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
	pip install h5py
    source deactivate
else
	echo "The environment will be setup using virtualenv"
	virtualenv -p /usr/bin/python3.6 $environment_name
	echo "export PYTHONPATH=`pwd`/src" >> "$environment_name/bin/activate"
	source "$environment_name/bin/activate"
	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
    pip install h5py	
fi

#build enviroment for server
python_path=`which python`
printf 'Python is installed at %s\n ' "$python_path"

environment_name_server="fhwa_faro_server"

if [[ "$python_path" =~ .*anaconda.* ]]; then
	echo "The environment will be setup using conda"
	env_path_server="${array[0]}envs/$environment_name_server"
    printf 'Path to conda environment created %s\n ' "$env_path_server"
    echo "....Creating Environment... Press y to continue"
    conda create -n $environment_name_server python=3.6
    echo "export PYTHONPATH=`pwd`/src:$PYTHONPATH" >> "$HOME/.bashrc"
    source activate $environment_name_server
    pip install h5py
    conda install -c anaconda cudnn
    pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
	pip install -U keras_vggface
	pip uninstall -y tensorflow-gpu tensorflow # this is installed by keras_vggface but we want the gpu version
	pip install -U tensorflow-gpu
	pip install -U keras==2.2.0 # The newer versions have a bug
	pip install -U dlib
	pip install mxnet-cu90
	pip install -U insightface
	
	source deactivate
else
	echo "The environment will be setup using virtualenv"
	virtualenv -p /usr/bin/python3.5 $environment_name_server
        echo "export PYTHONPATH=`pwd`/src" >> "$environment_name_server/bin/activate"
        source "$environment_name_server/bin/activate"
	pip install -U protobuf grpcio grpcio.tools pyvision_toolkit
	pip install -U keras_vggface
	pip uninstall -y tensorflow-gpu tensorflow # this is installed by keras_vggface but we want the gpu version
	pip install -U tensorflow-gpu
	pip install -U keras==2.2.0 # The newer versions have a bug
	pip install mxnet-cu90
        pip install -U insightface
	pip install -U dlib
    pip install h5py
fi


