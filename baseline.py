
from pathlib import Path
from PIL import Image
import csv

# Your image folder
image_folder = Path(r"D:\Final_Year_Project\Images")

# Folder to save compressed images and results
results_folder = Path(r"D:\Final_Year_Project\Results")
results_folder.mkdir(parents=True, exist_ok=True)

records = []

# Process all JPG and JPEG images
image_files = [
    p for p in image_folder.iterdir()
    if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg")
]

if not image_files:
    print("No JPG/JPEG images found. Check the folder path.")
else:
    for image_path in image_files:
        output_path = results_folder / (
            image_path.stem + "_compressed.jpg"
        )

        with Image.open(image_path) as img:
            img.convert("RGB").save(
                output_path,
                format="JPEG",
                quality=40,
                optimize=True
            )

        original_size = image_path.stat().st_size
        compressed_size = output_path.stat().st_size

        reduction = (
            (original_size - compressed_size)
            / original_size
        ) * 100

        records.append({
            "Image": image_path.name,
            "Original Bytes": original_size,
            "Compressed Bytes": compressed_size,
            "Reduction (%)": round(reduction, 2)
        })

        print(f"\nImage: {image_path.name}")
        print(f"Original size: {original_size:,} bytes")
        print(f"Compressed size: {compressed_size:,} bytes")
        print(f"Size reduction: {reduction:.2f}%")

    # Save measurements to CSV
    csv_path = results_folder / "baseline_results.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Image",
                "Original Bytes",
                "Compressed Bytes",
                "Reduction (%)"
            ]
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"\nResults saved to: {csv_path}")
