#!/bin/bash

#This script will setup the environment using conda or virtualenv.
#This will be dependent on where it finds the python installation (cmd:which python)

#author : Joel Brogan
#date : 02/10/2019
#@ORNL

#build enviroment for arcface.  ALSO REQUIRES NCCL
python_path=`which python3`
USE_VENV=1
if [ -z "$1" ]
  then
      echo "No venv argument supplied [argument 1]"
      USE_VENV=0
fi

printf 'Python is installed at %s\n ' "$python_path"

environment_name_server="env_arcface_gpu"

echo "The environment will be setup using built-in venv"
if [ -z "$USE_VENV" ]
then
    
    python -m venv $environment_name_server
    source "$environment_name_server/bin/activate"
fi
pip install -r ../../requirements.txt
curdir=`pwd`
echo $curdir
cd ../../
pip install .
#pip install numpy==1.23.5
cd $curdir
#pip install mxnet-cu114 #change to your version of cuda (e.g. -cu90)
#pip install insightface==0.1.5
pip install torch torchvision torchaudio
pip install scikit-image matplotlib pandas scikit-learn
RUN git clone https://github.com/mk-minchul/AdaFace.git
pip install tqdm bcolz-zipline prettytable menpo mxnet opencv-python
pip install pytorch-lightning==1.8.6
pip install h5py
sh ./download_models.sh

