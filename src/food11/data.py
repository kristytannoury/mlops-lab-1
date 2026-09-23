from pathlib import Path
from PIL import Image
import shutil

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

        class_number = file.name.split("_")[0]

        if class_number not in categories:
            continue

        category = categories[class_number]

        output_folder = processed_folder / split / category
        mini_output_folder = mini_folder / split / category

        output_folder.mkdir(parents=True, exist_ok=True)
        mini_output_folder.mkdir(parents=True, exist_ok=True)

        with Image.open(file) as img:
            img = img.convert("RGB")
            img = img.resize((128, 128))

            img.save(output_folder / file.name)

            if counts[category] < 100:
                img.save(mini_output_folder / file.name)
                counts[category] += 1

print("Data preparation finished.")