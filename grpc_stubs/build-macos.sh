#!/bin/bash

if [ ! -f protoc ]; then
    get https://packages.grpc.io/archive/2019/11/6950e15882f28e43685e948a7e5227bfcef398cd-6d642d6c-a6fc-4897-a612-62b0a3c9026b/protoc/grpc-protoc_macos_x64-1.26.0-dev.tar.gz
    tar zxvf grpc-protoc_macos_x64-1.26.0-dev.tar.gz
fi

# build cpp
mkdir cpp
./protoc -I ../proto --cpp_out=cpp --grpc_out=cpp --plugin=protoc-gen-grpc=./grpc_cpp_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build csharp
mkdir csharp
./protoc -I ../proto --csharp_out=csharp --grpc_out=csharp --plugin=protoc-gen-grpc=./grpc_csharp_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto
#./protoc -I ../proto --csharp_out=csharp --grpc_out=csharp --csharp_opt=base_namespace=FaRO --plugin=protoc-gen-grpc=./grpc_csharp_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build java
#mkdir java
#./protoc -I ../proto --java_out=java --grpc_out=java --plugin=protoc-gen-grpc=./grpc_java_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build python
mkdir python
./protoc -I ../proto --python_out=./python --grpc_out=./python --plugin=protoc-gen-grpc=./grpc_python_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build ruby
mkdir ruby
./protoc -I ../proto --ruby_out=./ruby --grpc_out=./ruby --plugin=protoc-gen-grpc=./grpc_ruby_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build ruby
mkdir php
./protoc -I ../proto --php_out=./php --grpc_out=./php --plugin=protoc-gen-grpc=./grpc_php_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build objc
mkdir objc
./protoc -I ../proto --objc_out=./objc --grpc_out=./objc --plugin=protoc-gen-grpc=./grpc_objective_c_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build go
#mkdir go
#./protoc -I ../proto --go_out=./go --grpc_out=./go faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto

# build node
mkdir js
./protoc -I ../proto --js_out=./js --grpc_out=./js --plugin=protoc-gen-grpc=./grpc_node_plugin faro/proto/face_service.proto faro/proto/geometry.proto faro/proto/image.proto





