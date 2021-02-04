#!/bin/bash

# Create and download some data if it does not exist.
if [ ! -d data ]; then

	mkdir data
	
	wget https://farm1.staticflickr.com/566/20522321974_ff107b5de1_z_d.jpg -O data/trump1.jpg
	wget https://farm5.staticflickr.com/4142/5440995682_c53756ae95_z_d.jpg -O data/trump2.jpg
	wget https://farm6.staticflickr.com/5730/30020836983_0c6d0e542e_z_d.jpg -O data/trump3.jpg
	#
	wget https://farm8.staticflickr.com/7207/6861189366_e204145def_z_d.jpg -O data/obama1.jpg
	wget https://farm3.staticflickr.com/2253/2125288685_0572f02e8a_z_d.jpg -O data/obama2.jpg
	wget https://farm4.staticflickr.com/3074/2414137667_b1d212a254_z_d.jpg -O data/obama3.jpg
	#
	wget https://farm7.staticflickr.com/6161/6172972931_53b0465c95_z_d.jpg -O data/bush1.jpg
	wget https://farm4.staticflickr.com/3073/2826871381_01cde64a19_b_d.jpg -O data/bush2.jpg
	wget https://farm4.staticflickr.com/3250/3050685683_8652f64593_z_d.jpg -O data/bush3.jpg

	wget https://www.army.mil/e2/c/images/2012/07/20/256785/size0.jpg -O data/children.jpg
	
	
	# These need to get fixed...
	# Transparent test
	#wget https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Trump_Circle.png/767px-Trump_Circle.png -O data/trump_trans.png
	
	# Gray test
	#wget https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Donald_Trump_August%2C19_2014%2C_head_only.png/565px-Donald_Trump_August%2C19_2014%2C_head_only.png -O data/trump_gray.png

fi

python -m faro.FaceClient detect -d detections.csv --detect-log=faces --face-log=faces data



