import argparse
from pathlib import Path
from xml.parsers.expat import model

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.models import ResNet18_Weights


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOTS = {
    "mini": PROJECT_ROOT / "data" / "food11_processed_mini",
    "processed": PROJECT_ROOT / "data" / "food11_processed",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Train ResNet18 on Food-11.")
    parser.add_argument(
        "--dataset",
        choices=["mini", "processed"],
        default="mini",
        help="Which processed Food-11 dataset to use.",
    )
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def make_dataloaders(dataset_root, batch_size):
    train_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    eval_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    train_dir = dataset_root / "training"
    val_dir = dataset_root / "validation"
    test_dir = dataset_root / "evaluation"

    for split_dir in (train_dir, val_dir, test_dir):
        if not split_dir.exists():
            raise FileNotFoundError(
                f"Expected dataset split not found: {split_dir}\n"
                "Check that your processed dataset contains "
                "'training', 'validation', and 'evaluation' folders."
            )

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=eval_transform)
    test_dataset = datasets.ImageFolder(test_dir, transform=eval_transform)

    if len(train_dataset.classes) != 11:
        raise ValueError(
            f"Expected 11 classes, but found {len(train_dataset.classes)} "
            f"in {train_dir}: {train_dataset.classes}"
        )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    return train_loader, val_loader, test_loader


def build_model():
    model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, 11)
    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    total_samples = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        batch_size = images.size(0)
        running_loss += loss.item() * batch_size
        total_samples += batch_size

    return running_loss / total_samples


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total_samples = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        batch_size = images.size(0)
        running_loss += loss.item() * batch_size
        total_samples += batch_size

        predictions = outputs.argmax(dim=1)
        correct += (predictions == labels).sum().item()

    avg_loss = running_loss / total_samples
    accuracy = correct / total_samples
    return avg_loss, accuracy


def main():
    args = parse_args()

    dataset_root = DATASET_ROOTS[args.dataset]
    device = get_device()

    print(f"Dataset: {dataset_root}")
    print(f"Device: {device}")

    train_loader, val_loader, test_loader = make_dataloaders(
        dataset_root,
        args.batch_size,
    )

    model = build_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # The training script is a separate Python process, so configure MLflow here.
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    with mlflow.start_run():
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
                "num_classes": 11,
                "device": str(device),
            }
        )

        for epoch in range(1, args.epochs + 1):
            train_loss = train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
            )
            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_loss, step=epoch)
            mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)

            print(
                f"Epoch {epoch}/{args.epochs} | "
                f"train_loss={train_loss:.4f} | "
                f"val_loss={val_loss:.4f} | "
                f"val_accuracy={val_accuracy:.4f}"
            )

        _, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        mlflow.log_metric("test_accuracy", test_accuracy)
        model = model.to("cpu")
        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle"
        )

        print(f"Final test accuracy: {test_accuracy:.4f}")


if __name__ == "__main__":
    main()
