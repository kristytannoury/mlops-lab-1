## Question 1
Without a volume, the data is stored inside the container. When we remove the container and create a new one, all the data is lost. The MLflow UI starts empty again.

## Question 2
A named volume is easier to manage and keeps the data separate from our project files. A bind mount would also work, but we would have to manage the folder ourselves.

## Question 3
In this lab, Docker Compose puts both containers on the same network and automatically resolves service names. Since our MLflow service is named mlflow, the other container can reach it using http://mlflow:5000 instead of host.docker.internal.

## Question 4
We use an environment variable to make the frontend flexible. Inside Docker Compose, we can use http://inference:8000, but if we run the frontend alone, that hostname won't resolve. We can then set a different URL without changing the code.

## Question 5
The inference service doesn't need to expose a port because only the frontend communicates with it. Docker Compose puts both containers on the same network, so the frontend can reach it using http://inference:8000

## Question 6
If MLflow isn't ready, the inference container fails to load the model and may crash. We can see the error using docker compose logs inference. We can fix this by adding a health check or a restart policy.

## Question 7
The frontend (8501) and MLflow (5001) have published ports. Inference doesn't have a published port because it communicates with the other containers through Docker's internal network. This matches our docker-compose.yml.

## Question 8

Before restarting, the frontend uses the old model version because serve.py loads the model only once at startup. To use the new Staging version, we run:

docker compose restart inference

## Question 9

Restart works because the model isn't stored inside the Docker image. The image contains the code and dependencies, while the model is fetched from MLflow at startup. So we don't need to rebuild the image.

## Question 10

After docker compose down and up, the registered model and its Staging alias are still there because the named volume keeps the data.

However, docker compose down -v also deletes the volume, so the MLflow database and artifacts are lost. When we start again, MLflow creates an empty database, and the registered model and Staging alias disappear.