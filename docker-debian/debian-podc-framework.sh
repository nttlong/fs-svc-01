#!/bin/bash
##--------------------------
# debian-py-39-app-framework
#------------------------------
helpFunction()
{
   echo "Please call with build number"
   exit 1 # Exit script after printing help
}

# Print helpFunction in case parameters are empty

if [ -z "$1" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi
docker_file=debian-py-39-app-framework
docker --log-level "info" buildx build \
      --build-arg REPO_LOCATION=$repositiory \
      --build-arg TAG="$1" \
      --build-arg USER=$user -t \
      $push/$docker_file:$generation  \
      --platform=$platform ./.. -f $docker_file  --push=true --output type=registry