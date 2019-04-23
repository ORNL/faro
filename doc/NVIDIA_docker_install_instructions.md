# Nvidia Docker Install Instructions

----------------------------------

The following are instructions on how to install Nvidia Docker to work with the FARO project.
These instructions were tested when installing on the deepblue machine.





1.	Go to https://github.com/NVIDIA/nvidia-docker

2.	Naviagate to 'QuickStart' portion of the documentation

3. 	Prereqs before install are the NVIDIA driver and a supported version of Docker
	*You can check for the prescence of the NVIDIA drive with the 'nvidia-smi' command


4.	Supported version of Docker install (Docker CE)
	Go to: https://docs.docker.com/install/linux/docker-ce/ubuntu/

5.	Navigate to 'Install using the repository' under the 'Install Docker CE' heading

6.	Follow the instructions above to install Docker CE (summary of commands below):


```
	sudo apt-get update
	sudo apt-get install apt-transport-https
	sudo apt-get install ca-certificates
	sudo apt-get install curl
	sudo apt-get install software-properties-common

	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

	sudo apt-key fingerprint 0EBFCD88 (NOTE: this confirms a valid fingerprint)

	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
	
	sudo apt-get update

	sudo apt-get install docker-ce

	sudo docker run hello-world (displays a message if everything went well)
```


7.	Go back to the page: https://github.com/NVIDIA/nvidia-docker

8.	Under 'Quickstart' follow Ubuntu 16.04 Instructions (summary of commands below):


```
	sudo docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f

	sudo apt-get purge -y nvidia-docker (if unable to locate package nvidia-docker its ok, this is just to remove old one if it exists)

	curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
	
	distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

	curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

	sudo apt-get update

	sudo apt-get install -y nvidia-docker2

	sudo pkill -SIGHUP dockerd

	sudo docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi  (note: this is a test and dumps outs nvidia-smi through docker)
```


9.	Navigate to faro/rcnn
```
	sudo ./build-docker.sh (note: takes several minutes)

	sudo ./run-docker.sh (note: takes several minutes)
```



NOTE: Some machines may have trouble with DNS name resolution in docker containers the solutions is as follows:
```
$ vi /etc/NetworkManager/NetworkManager.conf
Comment out this: #dns=dnsmasq
$ sudo systemctl restart network-manager
```



