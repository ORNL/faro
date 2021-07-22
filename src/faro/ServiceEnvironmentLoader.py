import os
import sys
import faro
import numpy as np
import subprocess
import faro.FaceService
import copy

try:
    import docker
except:
    print("Warning: Docker SDK is not installed. This will prevent FaRO from loading Docker images. (Install via `pip install docker`)")
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

def buildFlags(parser,options,service_instance_name=None,ignore=[]):

    flags = vars(options)
    cmd =[]
    for opts in [parser._long_opt,parser._short_opt]:
        optdict = {opts[k].dest: k for k in opts}
        for f in flags:  # f will be the opt_string
            if f not in ignore and f in optdict and optdict[f] not in ignore:
                if f in optdict:
                    op = str(flags[f])
                    if op != "None" and op != "":
                        cmd.append(optdict[f])
                        if op != "True" and op != "False":  # don't add option if it is just a bool
                            cmd.append(op)
    if service_instance_name is not None:
        cmd.append('--service-name')
        cmd.append(service_instance_name)
    return cmd

def startByVenv(options,service_instance_name,service_dir):
    prefix = "env_"
    build_prefix = "build_env_"
    environment_folder_path = prefix + options.algorithm
    buildscripts = []
    env_dirs = []
    for ntry in range(2): #We try twice, since the first time around might be the build process
        for d in os.listdir(service_dir):
            fpath = os.path.join(service_dir,d)
            if d.startswith(prefix+options.algorithm) and os.path.isdir(fpath):
                if options.verbose:
                    print('Found an environment directory ',d)
                env_dirs.append(os.path.join(service_dir,d))
            elif d.startswith(build_prefix+options.algorithm) and os.path.isfile(fpath):
                if options.verbose:
                    print('Found a build script to generate an environment: ', d)
                buildscripts.append(os.path.join(service_dir,d))

        if len(env_dirs) > 0:
            envnum=0
            if len(env_dirs) > 1:
                print('Found multiple environments. Please select one (default 0):')
                select_string = " ".join(["("+str(i)+")"+os.path.basename(d) for i,d in enumerate(env_dirs)])
                print(select_string)
                envnum = input()
                if envnum == "":
                    print('selecting default')
                    envnum = "0"
                while int(envnum) >= len(env_dirs):
                    print('Please Select a number 0 -',len(env_dirs)-1)
                    envnum = input()

                print('Running environment located in ', env_dirs[0])
            envdir = env_dirs[int(envnum)]
            activateFile = os.path.join(envdir,'bin','activate')
            if os.path.isdir(envdir) and os.path.exists(activateFile):
                if options.verbose:
                    print('the environment activation script has been found')
            if sys.platform == "linux" or sys.platform == "linux2":
                call = ". "
            elif sys.platform == "darwin":
                call = "source"
            else:
                call = "source"
            face_worker_list,parser= faro.FaceService.addServiceOptionsGroup() #Get only the service options so we know which ones to parse out
            cmdflags = buildFlags(parser,options,service_instance_name)
            # cmd = ["source", activateFile, "&&", "python", "-m", "faro.FaceService", "--port="+options.port, "--worker-count="+str(options.num_workers), "--algorithm="+options.algorithm, "--max-message-size="+str(-1 ), "--service-name",service_instance_name]
            cmd = [call, activateFile, "&&", "python", "-m", "faro.FaceService"]
            cmd.extend(cmdflags)

            print(" ".join(cmd))
            os.system(" ".join(cmd))
            break
        elif len(buildscripts) > 0 and ntry < 1:
            envnum=0
            if len(buildscripts) > 1:
                print("Found multiple build files. Please select one (default 0):")
                select_string = " ".join(["(" + str(i) + ")" + os.path.basename(d) for i, d in enumerate(buildscripts)])
                print(select_string)
                envnum = input()
                if envnum == "":
                    print('selecting default')
                    envnum = "0"
                while int(envnum) >= len(buildscripts):
                    print('Please Select a number 0 -', len(buildscripts) - 1)
                    envnum = input()
            buildscript = buildscripts[int(envnum)]
            os.system("cd "+ service_dir + " && " + buildscript)
        else:
            print('No environments or environment build scripts found for', options.algorithm ,".  Please create a build script titled 'build_env_'", options.algorithm," and place it in the respective service directory")
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
    elif docker_image_name not in images:
        print('No images by the name of',docker_image_name,' or containers were found in Docker. Building dockerfile instead')
        buildDockerFile(os.path.join(service_dir), docker_image_name)
    if docker_image_name in images:
        print('we found an uninstantiated docker image named ', docker_image_name)
        host = options.port.split(':')
        hostport = int(host[1])
        host = host[0]
        face_worker_list, parser = faro.FaceService.addServiceOptionsGroup()
        # command = "python -m faro.FaceService --port=" + "0.0.0.0:50030" + " --service-name="+ service_instance_name + " --worker-count="+ str(options.num_workers) + " --algorithm=" + options.algorithm
        command = ["python","-m", "faro.FaceService", "--port", "0.0.0.0:50030"]
        cmdflags = buildFlags(parser,options,service_instance_name,ignore=['port'])
        command.extend(cmdflags)

        if options.verbose:
            print(command)
        networkmode = "host"
        if sys.platform == "linux" or sys.platform == "linux2":
            networkmode = "host"
        elif sys.platform == "darwin":
            networkmode = "bridge"
        ports={50030:hostport}
        # network_mode=networkmode
        client.containers.run(docker_image_name, command,network_mode="bridge",ports={50030:hostport},stdout=True,remove=True,name=docker_instance_name,privileged=True)
    else:
        print('Even after building, no images were found in Docker by the name of', docker_image_name,', or containers by the name of ',docker_instance_name,'. Are you sure you named the docker worker correctly?')

def startByNative(options,service_instance_name,service_dir):
    options_copy = copy.copy(options)
    options_copy.service_name = service_instance_name
    faro.FaceService.serve(options)

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
