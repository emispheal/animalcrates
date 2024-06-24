echo "Running container..."
sudo docker ps -q

docker login --username AWS --password $(aws ecr get-login-password --region ap-southeast-2) 519948377493.dkr.ecr.ap-southeast-2.amazonaws.com
docker run --name flask_app -d -p 5000:5000 519948377493.dkr.ecr.ap-southeast-2.amazonaws.com/app-ecr-v1:latest