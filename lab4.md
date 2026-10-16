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