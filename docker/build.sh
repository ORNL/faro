#!/bin/bash


docker build -t faro_face_recognition_services .


######################### Useful commands ########################
# 1. Ensure that nvidia-docker is installed
# 2. run server - 
#       docker run --runtime=nvidia -it --net host -v $HOME/faro_storage:/faro/faro_storage:rw --name server faro_face_recognition_services
# 3. run client - 
#       docker run --runtime=nvidia -it --net host -v $HOME/faro_storage:/faro/faro_storage:rw --name client faro_face_recognition_services
# 4. The above two commands should be run in  separte terminals as it will create an interactive session.
# 5. In the server terminal,
#       - cd services
#       - cd dlib ; ./run_dlib.sh
#       - or
#       - cd vggface ; ./run_vggface.sh
#       - or
#       - cd arcface ; ./run_arcface.sh
# 6. in the client window,
#       - cd tests
#       - run the test code

#once done you can exit out of docker interactive mode
# by running the "exit" command.
# The docker server and client conatiners are stull running. So run the following commands
# 7. docker stop server
# 8. docker stop client
# Next, time you want to start the server and client containers in interactive mode then run the 
#following commands,
# 9. docker start server
# 10. docker start client
# 11. In terminal 1: docker exec -it server /bin/bash 
# 12. In terminal 2: docker exec -it client /bin/bash 
# then go back to steps , 5 and below.


#Note: server and client are docker conatiner names defined by the user. It camn be anything.
# the docker image built has the name : faro_face_recognition_services
# This is set in the build file.

