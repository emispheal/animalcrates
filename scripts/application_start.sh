echo "Running container..."
docker run --name app-ecr-v1 -d -p 5000:5000 519948377493.dkr.ecr.ap-southeast-2.amazonaws.com/app-ecr-v1:latest