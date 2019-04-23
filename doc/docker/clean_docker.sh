#!/bin/bash

docker kill $(docker ps -q)
docker rm $(docker ps --filter=status=exited --filter=status=created -q)
docker rmi $(docker images -a --filter=dangling=true -q)
docker rmi $(docker images -a -q)

