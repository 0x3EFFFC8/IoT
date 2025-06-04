#!/usr/bin/env bash
# stop script on error
set -e

# Check for python 3
if ! python3 --version &> /dev/null; then
  printf "\nERROR: python3 must be installed.\n"
  exit 1
fi

# Check to see if root CA file exists, download if not
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# Check to see if AWS Device SDK for Python exists, download if not
if [ ! -d ./aws-iot-device-sdk-python-v2 ]; then
  printf "\nCloning the AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python-v2.git --recursive
fi

# Check to see if AWS Device SDK for Python is already installed, install if not
if ! python3 -c "import awsiot" &> /dev/null; then
  printf "\nInstalling AWS SDK...\n"
  python3 -m pip install ./aws-iot-device-sdk-python-v2
  result=$?
  if [ $result -ne 0 ]; then
    printf "\nERROR: Failed to install SDK.\n"
    exit $result
  fi
fi

# Generate gRPC code from protobuf
if [ ! -f "./aws-iot-device-sdk-python-v2/samples/sensors_pb2.py" ] || [ ! -f "./aws-iot-device-sdk-python-v2/samples/sensors_pb2_grpc.py" ]; then
  printf "\nGenerating gRPC code...\n"
  python3 -m grpc_tools.protoc -I./aws-iot-device-sdk-python-v2/samples \
  --python_out=./aws-iot-device-sdk-python-v2/samples \
  --grpc_python_out=./aws-iot-device-sdk-python-v2/samples/ ./aws-iot-device-sdk-python-v2/samples/sensors.proto
fi 

# run gateway sample app using certificates downloaded in package
printf "\nRunning gateway sample application...\n"
python3 aws-iot-device-sdk-python-v2/samples/gateway.py --endpoint a2x7qtj0zxpnji-ats.iot.us-east-1.amazonaws.com --ca_file root-CA.crt --cert Gateway_Colombia_GW100.cert.pem --key Gateway_Colombia_GW100.private.key 
