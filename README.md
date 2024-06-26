![tests passing](https://github.com/emispheal/animalcrates/actions/workflows/python-app.yml/badge.svg?branch=master)

# Animal Crates
![logo](https://raw.githubusercontent.com/emispheal/animalcrates/master/animalcrateslogo.png)

## This Repo
This is animal crates' backend server running on Flask. 
The client repo running on Unity can be found at: https://github.com/emispheal/someslots/tree/master 

## The Game
Animal crates is a 5x5 cascade slots demo game with a respins feature.

## CI/CD
Below is a diagram of the the CI/CD pipeline used for this project. 
AWS Code Pipeline watches for changes to the protected master branch and then sends it to CodeBuild to build the docker image.
This image and its build artifacts are then sent to an s3 bucket. CodeDeploy can then compare its current and previous artifacts to see if a new
deployment is necessary. If a new deployment is in order, it can then be deployed to the single EC2 running instance. 

![pipeline](https://raw.githubusercontent.com/emispheal/animalcrates/master/pipeline.png)

