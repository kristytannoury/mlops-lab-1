
import shutil
from pathlib import Path

from PIL import Image

categories = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}

CLASSES = list(categories.values())


def category_from_filename(filename: str) -> str | None:
    class_number = filename.split("_")[0]
    return categories.get(class_number)


def resize_image(img: Image.Image, size: int = 128) -> Image.Image:
    """Return an RGB image resized to ``size`` by ``size`` pixels."""
    return img.convert("RGB").resize((size, size))


def main():
    raw_folder = Path("data/food11_raw")
    processed_folder = Path("data/food11_processed")
    mini_folder = Path("data/food11_processed_mini")

    # Delete old processed folders if they already exist
    if processed_folder.exists():
        shutil.rmtree(processed_folder)

    if mini_folder.exists():
        shutil.rmtree(mini_folder)

    splits = ["training", "evaluation", "validation"]

    for split in splits:
        counts = {category: 0 for category in categories.values()}

        for file in sorted((raw_folder / split).iterdir()):
            if not file.is_file():
                continue

            category = category_from_filename(file.name)

            if category is None:
                continue

            output_folder = processed_folder / split / category
            mini_output_folder = mini_folder / split / category

            output_folder.mkdir(parents=True, exist_ok=True)
            mini_output_folder.mkdir(parents=True, exist_ok=True)

            with Image.open(file) as img:
                img = resize_image(img)

                img.save(output_folder / file.name)

                if counts[category] < 100:
                    img.save(mini_output_folder / file.name)
                    counts[category] += 1

    print("Data preparation finished.")


if __name__ == "__main__":
    main()
