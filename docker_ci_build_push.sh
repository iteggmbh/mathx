#!/bin/bash

IMAGEBASE="mathx"
IMAGE="$CI_REGISTRY_IMAGE/$IMAGEBASE"
HARBORIMAGE="harbor.iteg.at/clazzesorg/$IMAGEBASE"

# evtl. move dist to allow putting web in .dockerignore
#test -d dist || mv -v web/dist .

docker pull python:3.12-alpine

docker build --no-cache=true \
  --tag $IMAGE:latest \
  --tag $HARBORIMAGE:latest \
  .

docker push $IMAGE:$IMAGETAG
docker push $IMAGE:latest

docker push $HARBORIMAGE:$IMAGETAG
docker push $HARBORIMAGE:latest

