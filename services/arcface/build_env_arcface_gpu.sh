#!/bin/bash

#This script will setup the environment using conda or virtualenv.
#This will be dependent on where it finds the python installation (cmd:which python)

#author : Joel Brogan
#date : 02/10/2019
#@ORNL

#build enviroment for arcface.  ALSO REQUIRES NCCL
python_path=`which python`
printf 'Python is installed at %s\n ' "$python_path"

environment_name_server="env_arcface_gpu"

echo "The environment will be setup using built-in venv"
python -m venv $environment_name_server
source "$environment_name_server/bin/activate"
pip install -r ../../requirements.txt
curdir=`pwd`
echo $curdir
cd ../../
python setup.py install
pip install numpy==1.23.5
cd $curdir
pip install mxnet-cu114 #change to your version of cuda (e.g. -cu90)
pip install insightface==0.1.5
pip install h5py

sh ./download_models.sh
