#!/bin/bash

#This script will setup the environment using conda or virtualenv.
#This will be dependent on where it finds the python installation (cmd:which python)

#author : Joel Brogan
#date : 02/10/2019
#@ORNL

#build enviroment for arcface.
python_path=`which python`
printf 'Python is installed at %s\n ' "$python_path"

environment_name_server="env_dlib_cpu"

echo "The dlib environment will be setup using built-in venv"
python -m venv $environment_name_server
source "$environment_name_server/bin/activate"
pip install -r ../../requirements.txt
curdir=`pwd`
echo $curdir
cd ../../
python setup.py develop
cd $curdir
pip install dlib
pip install h5py

./download_models.sh


