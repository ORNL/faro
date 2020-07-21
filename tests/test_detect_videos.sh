#!/bin/bash

#Author : Nisha Srinivas
#Date : 05/24/2020

# Create and download some data if it does not exist.
if [ ! -d data_videos ]; then

	mkdir data_videos
	
	wget https://obamawhitehouse.archives.gov/videos/2011/January/012511_ITWH_SOTU.mp4 -O data_videos/state_of_union.mp4
	wget https://obamawhitehouse.archives.gov/videos/2012/February/020712_Marshmallow_Launch.mp4  -O data_videos/marshmellow_lauch.mp4

fi

python -m faro detect -d detections_videos.csv --detect-log=detect_videos --face-log=faces_videos data_videos



