import io
import os

import mlflow
import torch
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from torchvision import transforms


app = FastAPI()

# Food11 classes
CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

# Same preprocessing used during validation/testing
transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)

# Get MLflow server address from environment variable
tracking_uri = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(tracking_uri)

# Load model only once when the server starts
model = mlflow.pyfunc.load_model("models:/food11@champion")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")

    image_tensor = transform(image)

    # Add batch dimension: [3, 224, 224] -> [1, 3, 224, 224]
    batch = image_tensor.unsqueeze(0)

    # Run the MLflow model
    predictions = model.predict(batch.numpy())

    # Convert output to tensor
    logits = torch.tensor(predictions)

    # Convert logits to probabilities
    probabilities = torch.softmax(logits, dim=1)

    confidence, predicted_index = torch.max(probabilities, dim=1)

    predicted_category = CLASSES[predicted_index.item()]

    return {
        "category": predicted_category,
        "confidence": confidence.item(),
    }