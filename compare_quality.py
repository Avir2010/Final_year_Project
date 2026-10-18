import numpy as np
from pathlib import Path
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import csv

PROJECT_DIR = Path(r"D:\Final_Year_Project")
IMAGE_DIR = PROJECT_DIR / "Images"
RESULTS_DIR = PROJECT_DIR / "results"
OUTPUT_DIR = RESULTS_DIR / "quality_comparison"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

qualities = [40, 60, 75, 85]
extensions = {".jpg", ".jpeg", ".png", ".webp"}
results = []

for image_path in sorted(IMAGE_DIR.iterdir()):
    if image_path.suffix.lower() not in extensions:
        continue

    with Image.open(image_path) as original:
        original_rgb = original.convert("RGB")
        original_size = image_path.stat().st_size

        for quality in qualities:
            output_path = (
                OUTPUT_DIR /
                f"{image_path.stem}_q{quality}.jpg"
            )

            original_rgb.save(
                output_path,
                "JPEG",
                quality=quality,
                optimize=True
            )

            compressed_size = output_path.stat().st_size

            reduction = (
                (original_size - compressed_size)
                / original_size * 100
            )

            with Image.open(output_path) as compressed:
                compressed_rgb = compressed.convert("RGB")

                score = ssim(
    np.array(original_rgb),
    np.array(compressed_rgb),
    data_range=255,
    channel_axis=2
)

            results.append({
                "Image": image_path.name,
                "Quality": quality,
                "Original Bytes": original_size,
                "Compressed Bytes": compressed_size,
                "Reduction (%)": round(reduction, 2),
                "SSIM": round(score, 4)
            })

            print(
                f"{image_path.name} | Q{quality} | "
                f"{compressed_size} bytes | "
                f"Reduction: {reduction:.2f}% | "
                f"SSIM: {score:.4f}"
            )

csv_path = RESULTS_DIR / "quality_comparison.csv"

with csv_path.open(
    "w", newline="", encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Image",
            "Quality",
            "Original Bytes",
            "Compressed Bytes",
            "Reduction (%)",
            "SSIM"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

print("\nComparison completed.")
print(f"Results saved to: {csv_path}")
print(f"Images saved to: {OUTPUT_DIR}")
