#!/bin/bash

set -e

timestamp=$(date +%Y%m%d%H%M)

echo building linux binary...

GOOS=linux GOARCH=amd64 go build -o entrypoint_linux entrypoint.go

echo building docker image...

docker build --no-cache -t fredhutch/ubuntu-with-batchit:$timestamp .

echo tagging docker image...

docker tag fredhutch/ubuntu-with-batchit:$timestamp fredhutch/ubuntu-with-batchit:latest

echo pushing docker image

docker push fredhutch/ubuntu-with-batchit:latest

echo Done
