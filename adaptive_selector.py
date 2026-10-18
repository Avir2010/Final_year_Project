
from pathlib import Path
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import numpy as np
import csv

PROJECT_DIR = Path(r"D:\Final_Year_Project")
IMAGE_DIR = PROJECT_DIR / "Images"
RESULTS_DIR = PROJECT_DIR / "results"
OUTPUT_DIR = RESULTS_DIR / "adaptive_output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

QUALITIES = [40, 60, 75, 85]
SSIM_THRESHOLD = 0.97
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

results = []

for image_path in sorted(IMAGE_DIR.iterdir()):
    if image_path.suffix.lower() not in EXTENSIONS:
        continue

    print(f"\nProcessing: {image_path.name}")

    with Image.open(image_path) as source:
        original = source.convert("RGB")
        original_size = image_path.stat().st_size
        candidates = []

        for quality in QUALITIES:
            candidate_path = (
                OUTPUT_DIR /
                f"{image_path.stem}_q{quality}.jpg"
            )

            original.save(
                candidate_path,
                "JPEG",
                quality=quality,
                optimize=True
            )

            candidate_size = candidate_path.stat().st_size

            with Image.open(candidate_path) as candidate:
                candidate_rgb = candidate.convert("RGB")

                score = ssim(
                    np.array(original),
                    np.array(candidate_rgb),
                    data_range=255,
                    channel_axis=2
                )

            reduction = (
                (original_size - candidate_size)
                / original_size * 100
            )

            candidates.append({
                "quality": quality,
                "path": candidate_path,
                "size": candidate_size,
                "ssim": float(score),
                "reduction": reduction
            })

            print(
                f"Q{quality}: {candidate_size} bytes, "
                f"SSIM={score:.4f}, "
                f"reduction={reduction:.2f}%"
            )

    # Keep only candidates that meet both requirements.
    valid = [
        item for item in candidates
        if item["ssim"] >= SSIM_THRESHOLD
        and item["size"] < original_size
    ]

    if valid:
        # Choose the smallest qualifying image.
        chosen = min(valid, key=lambda item: item["size"])
        chosen_quality = chosen["quality"]
        chosen_size = chosen["size"]
        chosen_ssim = chosen["ssim"]
        final_path = OUTPUT_DIR / f"{image_path.stem}_adaptive.jpg"

        final_path.write_bytes(chosen["path"].read_bytes())
        decision = f"JPEG quality {chosen_quality}"
        reduction = chosen["reduction"]

    else:
        # No candidate met both requirements.
        chosen_quality = "Original"
        chosen_size = original_size
        chosen_ssim = 1.0
        reduction = 0.0
        final_path = OUTPUT_DIR / f"{image_path.stem}_adaptive{image_path.suffix}"
        final_path.write_bytes(image_path.read_bytes())
        decision = "Original retained"

    print(f"Decision: {decision}")
    print(f"Final size: {chosen_size} bytes")
    print(f"Final output: {final_path.name}")

    results.append({
        "Image": image_path.name,
        "Decision": decision,
        "Original Bytes": original_size,
        "Final Bytes": chosen_size,
        "Reduction (%)": round(reduction, 2),
        "SSIM": round(chosen_ssim, 4),
        "Output File": final_path.name
    })

csv_path = RESULTS_DIR / "adaptive_results.csv"

with csv_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Image", "Decision", "Original Bytes",
            "Final Bytes", "Reduction (%)", "SSIM",
            "Output File"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

total_original = sum(r["Original Bytes"] for r in results)
total_final = sum(r["Final Bytes"] for r in results)
total_reduction = (
    (total_original - total_final) / total_original * 100
    if total_original else 0
)

print("\n" + "=" * 45)
print("ADAPTIVE SELECTOR SUMMARY")
print("=" * 45)
print(f"Images processed: {len(results)}")
print(f"Original total: {total_original} bytes")
print(f"Final total: {total_final} bytes")
print(f"Overall reduction: {total_reduction:.2f}%")
print(f"Results CSV: {csv_path}")
