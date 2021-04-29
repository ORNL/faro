#!/bin/bash

#Python
python -m grpc_tools.protoc --python_out=src --grpc_python_out=src --proto_path=proto faro/proto/image.proto faro/proto/geometry.proto faro/proto/face_service.proto faro/proto/string_int_label_map.proto 

#C++
#protoc -I proto --cpp_out=include image_read.proto face_service.proto geometry.proto image.proto
#protoc -I proto --grpc_out=include --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` image_read.proto face_service.proto geometry.proto image.proto

 echo proto build complete.
