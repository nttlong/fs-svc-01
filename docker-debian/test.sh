#!/bin/bash
helpFunction()
{
   echo ""
   echo "Please call with build number"
   exit 1 # Exit script after printing help
}

# Print helpFunction in case parameters are empty

if [ -z "$1" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi
echo "$1"
