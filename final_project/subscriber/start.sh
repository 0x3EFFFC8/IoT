#!/usr/bin/env bash
# Script to start MQTT subscriber and store data in PostgreSQL

# Stop script on error
set -e

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    printf "\nERROR: Python 3 is not installed. Please install it first.\n"
    exit 1
fi

# Download AWS IoT root certificate if it doesn't exist
if [ ! -f ./root-CA.crt ]; then
    printf "\nDownloading AWS IoT Root CA certificate...\n"
    curl -sS https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# Clone AWS IoT Device SDK if it doesn't exist
if [ ! -d ./aws-iot-device-sdk-python-v2 ]; then
    printf "\nCloning AWS IoT Device SDK for Python...\n"
    git clone --quiet https://github.com/aws/aws-iot-device-sdk-python-v2.git --recursive
fi

# Install the SDK if not installed
if ! python3 -c "import awsiot" &> /dev/null; then
    printf "\nInstalling AWS IoT Device SDK...\n"
    if ! python3 -m pip install --quiet ./aws-iot-device-sdk-python-v2; then
        printf "\nERROR: Failed to install SDK.\n"
        exit 1
    fi
fi

# Run the subscription application
printf "\nStarting MQTT subscription application...\n"
python3 aws-iot-device-sdk-python-v2/samples/subs.py --endpoint a2x7qtj0zxpnji-ats.iot.us-east-1.amazonaws.com --ca_file root-CA.crt --cert Gateway_Colombia_GW100.cert.pem --key Gateway_Colombia_GW100.private.key --client_id basicSub
