import os
import sys
import faro
import numpy as np
import subprocess
try:
    import docker
except:
    print("Warning: Docker SDK is not installed. This will prevent FaRO from loading Docker images. Run `pip install docker`")
    docker = None



def detectDocker(serviceName):
    if docker is not None:
        #step 1: is there a running docker container?
        client = docker.from_env()
        containerList = client.containers.list()
        imageList = client.images.list()

def detectImage(serviceName):
    serviceName = serviceName.lower()

    if docker is not None:
        client = docker.from_env()
        imageList = client.images.list()
        relevantImages = []
        for dimage in imageList:
            repotags = dimage.attrs['RepoTags']
            for tag in repotags:
                parts = tag.split(':')
                name = parts[0]
                tag = parts[1]
                if serviceName in name:
                    relevantImages.append(dimage)
        if len(relevantImages) > 0:
            print('Found ', len(relevantImages), ' Docker images:')
            [print(im.attrs['RepoTags']) for im in relevantImages]



def startByDocker(options,service_instance_name,service_dir):
    prefix = "faro_"
    docker_instance_name = prefix+service_instance_name
    docker_image_name = prefix+options.algorithm
    containers = getDockercontainers()
    images = getDockerImages()
    client = docker.from_env()
    print('looking for containers named ',docker_instance_name)
    print('looking for images named ', docker_image_name)
    if docker_image_name not in images and docker_instance_name not in containers:
        print('No images or containers were found in Docker. Building dockerfile instead')
        buildDockerFile(os.path.join(service_dir), docker_image_name)
    containers = getDockercontainers()
    images = getDockerImages()
    if docker_instance_name in containers:
        print('we found a container called ', docker_instance_name)
        containerstatus = containers[docker_instance_name].attrs['State']['Status']
        if containerstatus.lower() == "paused":
            #we need to start the container
            print('we should start the container')
            pass
        else:
            #we need to do nothing
            print('we are already done')
            pass
    elif docker_image_name in images:
        print('we found an uninstantiated docker image named ', docker_image_name)
        host = options.port.split(':')
        hostport = int(host[1])
        host = host[0]
        command = "python -m faro.FaceService --port=" + "0.0.0.0:50030" + " --service-name="+ service_instance_name + " --worker-count="+ str(options.num_workers) + " --algorithm=" + options.algorithm
        if options.verbose:
            print(command)
        networkmode = "host"
        if sys.platform == "linux" or sys.platform == "linux2":
            networkmode = "host"
        elif sys.platform == "darwin":
            networkmode = "bridge"
        #     ports={50030:hostport}
        # network_mode=networkmode
        client.containers.run(docker_image_name, command,stdout=True,remove=True,name=docker_instance_name,privileged=True)
    else:
        print('Final: No images or containers were found in Docker. Building dockerfile instead')
        buildDockerFile(os.path.join(service_dir),docker_image_name)




def getDockercontainers():
    if docker is not None:
        client = docker.from_env()
        # first, see if a docker container exists
        containerList = client.containers.list()
        return {c.attrs['Name'][1:]:c for c in containerList}
    return {}

def getDockerImages():
    prefix = "faro_"
    imdict = {}
    if docker is not None:
        client = docker.from_env()
        imageList = client.images.list()
        relevantImages = []
        for dimage in imageList:
            repotags = dimage.attrs['RepoTags']
            alltags = []
            for tag in repotags:
                parts = tag.split(':')
                name = parts[0]
                tag = parts[1]
                alltags.append(name)
            if len(alltags) > 0:
                imdict[alltags[0]] = dimage
    return imdict

def buildDockerFile(filePath,tag):
    if os.path.isdir(filePath):
        cmd = ["docker", "build","-t", tag, filePath]
        print(" ".join(cmd))
        os.system(" ".join(cmd))
        # process = subprocess.Popen(["docker", "build", "--no-cache" ,"-t", tag, filePath],stdout=subprocess.PIPE,
        #                        stderr=subprocess.PIPE)
        # # for line in iter(process.stdout.readline, b''):
        # #     print(line)
        # response, err = process.communicate()
        # process.stdout.close()
        # print(response)
        # errcode = process.returncode
        # if errcode is not 0:
        #     print(err)
        print('done')
