## Question 1

My registered model was given version 1. A logged model artifact is the model saved as part of a specific MLflow run, while a registered model is added to the Model Registry with a name and version number so it can be managed and versioned more easily.

## Question 2

MLflow replaced the old built-in stages such as Staging, Production, and Archived with model aliases. Model versions are separate from runs so the registered model can have its own history and be managed independently from the experiment run that produced it. Aliases are more flexible because they can have custom names, such as champion or challenger, and can easily be reassigned to different model versions.

## Question 3

I loaded the model using models:/food11@champion instead of a direct .pth path because MLflow manages the registered model and its version for me. This made it possible for my FastAPI app to load the correct model and successfully return a prediction for the Bread image with about 86.6% confidence.

To serve a newer model version, I would only need to move the champion alias to that newer version in MLflow. I would not need to change the path in serve.py, because it would still load models:/food11@champion.

## Question 4

We copy pyproject.toml and uv.lock first so Docker can cache the dependencies. If I only change serve.py, it does not reinstall everything.

## Question 5

The naive image was 9.01 GB and the multi-stage image was 1.87 GB, so the difference was about 7.14 GB. The biggest layers were COPY . . in the naive image and the virtual environment in the multi-stage image.

## Question 6

Without .dockerignore, Docker sends unnecessary files to the build context, so builds are slower and the image can become much bigger. In my case, folders like .venv/, data/, and mlruns/ are very large. .venv/ can also cause problems because it contains files built for my Mac, not for the Linux container.

## Question 7

127.0.0.1 inside the container refers to the container itself, not my Mac. host.docker.internal points to the host machine, so the container can reach MLflow running on my Mac.

## Question 8

Yes, it still loads correctly without rebuilding. This shows that the app and dependencies are inside the image, while the model is loaded from MLflow at runtime.

## Question 9

The Dockerfile is in Git, but the actual Docker image is still only on my laptop. To let another machine run the exact same image, I need to push the image to a container registry like Docker Hub or GitHub Container Registry and tag it with a fixed version.