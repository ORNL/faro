## FARO - Installation Notes
------------------------------------

** These notes are old and sholud bprobably be ignored for now. **


1.	Clone repo
2.	Build the environment:
```
	./build-env.sh
```
3.	Build necessary grpc files:
```
	./build.sh
```
4.	Install Nvidia docker:

	*see project top level file "NVIDIA_docker_install_instructions"

	* if you get an error from last command about a port already allocated run:
	sudo docker ps
	* this will show if something is using the port (50030 is default currently)
	* if there is note the Container ID number and run:
	sudo docker kill CONTAINER_ID

5. 	the last command will end with "worker process ready"
	leave this terminal alone, it is the server



## FARO - Useage
----------------

1.	Open a new terminal and navigate to top level folder
2.	`source the environment:
	source env_orj\bin\activate ????`

2.	`cd \bin`

3.	run `python face_detect_client.py` to see usage

NOTE: Make sure to kill the server running with Ctrl+C so as to avoid leaving that port listening and causing conflicts
