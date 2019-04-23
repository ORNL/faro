 2093  git clone --recursive https://github.com/rbgirshick/py-faster-rcnn.git
 2094  cd py-faster-rcnn/lib
 2095  make -j8
 2096  pip install cython
 2097  make -j8
 2098  source ../../../../env_faro_server2/
 2099  source ../../../../env_faro_server2/bin/activate
 2100  make -j8
 2101  pip install cython
 2102  ls
 2103  make -j8
 2104  cd ../caffe-fast-rcnn/
 2105  cp Makefile.config.example Makefile.config
# this line does not work because new lines are not added correctly
# this needs to have the correct version of cudnn --> x86_64-linux-gnu/cudnn_v6.h
2106  echo "\nWITH_PYTHON_LAYER := 1\nUSE_CUDNN := 1\n" >> Makefile.config
 2107  make -j8 
 2108  sudo apt install hdf5-tools 
 2109  sudo apt autoremove 
 2110  sudo apt install libhdf5-dev 
 2111  make -j8 
 2112  ls /usr/include/hdf5/
 2113  INCLUDEPATH=/usr/include/hdf5/serial make -j8 
 2114  INCLUDEPATH=/usr/include/hdf5/serial make 
 2115  vi Makefile.config
# replace hdf5.h with hdf5/serial/hdf5.h 
2116  vi src/caffe/layers/hdf5_data_layer.cpp
 2117  make
 2118  vi ./include/caffe/layers/hdf5_data_layer.hpp
 2119  make
 2120  vi ./include/caffe/layers/hdf5_data_layer.hpp
 2121  make
 2122  vi ./include/caffe/util/hdf5.hpp
 2123  ls
 2124  vi ./include/caffe/util/hdf5.hpp
 2125  make
 2126  vi src/caffe/layers/hdf5_output_layer.cpp
 2127  make
 2128  vi .
 2129  vi ./include/caffe/layers/hdf5_output_layer.hpp
 2130  make
 2131  make -j 8
 2132  vi src/caffe/net.cpp
 2133  make -j 8
 2134  vi Makefile
 2135  vi Makefile.config
 2136  make -j 8
 2137  vi src/caffe/layers/hdf5_data_layer.cu
 2138  make -j 8
 2139  vi src/caffe/layers/hdf5_output_layer.cu
 2140  make -j 8
 2141  cat Makefile.config | grep hdf5
 2142  cat Makefile | grep hdf5
 2143  cat Makefile | grep hdf5 -n
 2144  vi Makefile
 2145  make
 2146  make -j8 pycaffe
 2147  ls
 2148  make -j8 pycaffe
 2149  ipython
 2150  make -j8 pycaffe
 2151  vi Makefile
 2152  make -j8 pycaffe
 2153  ls
 2154  cd build
 2155  ls
 2156  cd ..
 2157  ls
 2158  cd ..
 2159  ls
 2160  export PYTHONPATH=$PYTHONPATH:`pwd`/py-faster-rcnn/lib/:`pwd`/py-faster-rcnn/caffe-fast-rcnn/python
 2161  python
 2162  ipython
 2163  ls
 2164  ./run-rcnn.sh 
 2165  pip install easydict
 2166  ./run-rcnn.sh 
 2167  cd py-faster-rcnn/
 2168  mkdir tmp
 2169  cd tmp/
 2170  ls

