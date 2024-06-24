#!/bin/bash

echo "Logging in to Amazon ECR..."
docker login --username AWS --password $(aws ecr get-login-password --region ap-southeast-2) 519948377493.dkr.ecr.ap-southeast-2.amazonaws.com
echo "Logged in to Amazon ECR successfully."

echo "Pulling image from Amazon ECR"
docker pull 519948377493.dkr.ecr.ap-southeast-2.amazonaws.com/app-ecr-v1:latest
echo "Pulled image from Amazon ECR successfully."