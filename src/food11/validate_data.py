"""Validate a processed Food-11 dataset before training or evaluation."""

import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image

CLASSES = {
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
}
SPLITS = ("training", "validation", "evaluation")


def validate(root: Path, min_per_class: int, tau: float) -> bool:
    counts = {split: {name: 0 for name in CLASSES} for split in SPLITS}
    seen = {}
    folder_ok = True
    image_ok = True
    minimum_ok = True
    duplicates_ok = True
    details = {key: [] for key in ("folders", "images", "minimum", "duplicates", "shares")}

    if not root.is_dir():
        details["folders"].append(f"Dataset folder not found: {root}")
        folder_ok = False

    for split in SPLITS:
        split_dir = root / split
        actual = {p.name for p in split_dir.iterdir() if p.is_dir()} if split_dir.is_dir() else set()
        if actual != CLASSES:
            folder_ok = False
            details["folders"].append(
                f"{split}: missing {sorted(CLASSES - actual)}, extra {sorted(actual - CLASSES)}"
            )
        if not split_dir.is_dir():
            image_ok = False
            minimum_ok = False
            continue

        for class_name in sorted(CLASSES):
            class_dir = split_dir / class_name
            if not class_dir.is_dir():
                minimum_ok = False
                continue

            for path in sorted(class_dir.iterdir()):
                if not path.is_file():
                    image_ok = False
                    details["images"].append(f"Unexpected non-file entry: {path}")
                    continue

                counts[split][class_name] += 1
                try:
                    with Image.open(path) as img:
                        if img.format is None:
                            raise ValueError("Unrecognized image format")
                        if img.mode != "RGB" or img.size != (128, 128):
                            image_ok = False
                            details["images"].append(
                                f"{path}: mode={img.mode}, size={img.size}"
                            )
                        img.load()  # Decode image data; catches truncated/corrupted files.
                except (OSError, ValueError) as exc:
                    image_ok = False
                    details["images"].append(f"Cannot read {path}: {exc}")

                try:
                    digest = hashlib.md5(path.read_bytes()).hexdigest()
                except OSError as exc:
                    duplicates_ok = False
                    details["duplicates"].append(f"Cannot hash {path}: {exc}")
                    continue

                original = seen.get(digest)
                if original is not None and original[0] != split:
                    duplicates_ok = False
                    details["duplicates"].append(f"{original[1]} <-> {path}")
                else:
                    seen.setdefault(digest, (split, path))

            count = counts[split][class_name]
            if count < min_per_class:
                minimum_ok = False
                details["minimum"].append(
                    f"{split}/{class_name}: {count} images (need {min_per_class})"
                )

    train_total = sum(counts["training"].values())
    valid_total = sum(counts["validation"].values())
    shares_ok = train_total > 0 and valid_total > 0
    if not shares_ok:
        details["shares"].append("Training or validation has no images")
    else:
        for class_name in sorted(CLASSES):
            train_share = counts["training"][class_name] / train_total
            valid_share = counts["validation"][class_name] / valid_total
            if abs(train_share - valid_share) > tau:
                shares_ok = False
                details["shares"].append(
                    f"{class_name}: training {train_share:.3f}, validation {valid_share:.3f}"
                )

    checks = (
        ("folders", "Exactly 11 class folders in each split", folder_ok),
        ("images", "All images open, are RGB and 128x128", image_ok),
        ("minimum", f"At least {min_per_class} images per class per split", minimum_ok),
        ("duplicates", "No duplicate image content across splits (MD5)", duplicates_ok),
        ("shares", f"Training/validation class shares within tau={tau:g}", shares_ok),
    )
    for key, description, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'} - {description}")
        if not passed:
            for item in details[key][:5]:
                print(f"  {item}")
            if len(details[key]) > 5:
                print(f"  ... and {len(details[key]) - 5} more")

    return all(passed for _, _, passed in checks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Processed dataset directory")
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)
    args = parser.parse_args()
    if args.min_per_class < 0 or not 0 <= args.tau <= 1:
        parser.error("--min-per-class must be >= 0 and --tau must be between 0 and 1")

    if not validate(args.dataset, args.min_per_class, args.tau):
        sys.exit(1)


if __name__ == "__main__":
    main()
