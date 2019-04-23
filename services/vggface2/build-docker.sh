#!/bin/bash

cp -r ../../src ./

docker build -t faro-vggface2 .
