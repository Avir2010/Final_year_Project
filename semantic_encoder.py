
import base64
import json
import time
from pathlib import Path

import requests

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_DIR = Path(r"D:\Final_Year_Project")
IMAGE_PATH = PROJECT_DIR / "Images" / "car.jpg"
RESULTS_DIR = PROJECT_DIR / "results"

MODEL = "qwen2.5vl:3b"
API_URL = "http://localhost:11434/api/generate"

OUTPUT_PATH = RESULTS_DIR / "car_semantics.json"

# --------------------------------------------------
# 2. Check the input image
# --------------------------------------------------

print("Step 1: Checking image...")

if not IMAGE_PATH.exists():
    print(f"ERROR: Image not found: {IMAGE_PATH}")
    raise SystemExit(1)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

original_size = IMAGE_PATH.stat().st_size

print(f"Image: {IMAGE_PATH.name}")
print(f"Original size: {original_size:,} bytes")

# --------------------------------------------------
# 3. Read and encode the image
# --------------------------------------------------

print("\nStep 2: Reading image...")

with open(IMAGE_PATH, "rb") as image_file:
    image_data = base64.b64encode(
        image_file.read()
    ).decode("utf-8")

print("Image loaded successfully.")

# --------------------------------------------------
# 4. Send the image to Qwen2.5-VL
# --------------------------------------------------

print("\nStep 3: Sending image to Qwen...")
print("Please wait. Inference may take several minutes.")

start_time = time.time()

try:
    response = requests.post(
        API_URL,
        json={
            "model": MODEL,
            "prompt": (
                "Analyze this image for bandwidth-efficient "
                "visual scene transmission. Describe the main "
                "objects, their colors, and the environment. "
                "Use no more than 25 words. Be factual and "
                "do not invent details."
            ),
            "images": [image_data],
            "stream": False,
            "keep_alive": 0
        },
        timeout=600
    )

    response.raise_for_status()
    result = response.json()

    description = result.get("response", "").strip()

    if not description:
        print("ERROR: Qwen returned an empty description.")
        raise SystemExit(1)

    inference_time = time.time() - start_time

    # --------------------------------------------------
    # 5. Save semantic information as JSON
    # --------------------------------------------------

    print("\nStep 4: Saving semantic information...")

    semantic_data = {
        "image": IMAGE_PATH.name,
        "model": MODEL,
        "description": description
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
        json.dump(
            semantic_data,
            output_file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------
    # 6. Calculate size reduction
    # --------------------------------------------------

    semantic_size = OUTPUT_PATH.stat().st_size

    # Positive value means smaller semantic data.
    size_reduction = (
        (original_size - semantic_size) / original_size
    ) * 100

    bytes_saved = original_size - semantic_size

    # --------------------------------------------------
    # 7. Display results
    # --------------------------------------------------

    print("\n" + "=" * 50)
    print("       SEMANTIC ENCODER RESULTS")
    print("=" * 50)

    print(f"\nInput image: {IMAGE_PATH.name}")
    print(f"AI model: {MODEL}")

    print("\nGenerated description:")
    print(description)

    print("\nFile-size comparison:")
    print(f"Original image:  {original_size:,} bytes")
    print(f"Semantic JSON:   {semantic_size:,} bytes")

    print(f"\nBytes saved: {bytes_saved:,}")
    print(f"Size reduction: {size_reduction:.2f}%")

    if semantic_size < original_size:
        print("Result: Semantic JSON is smaller than the image.")
    elif semantic_size == original_size:
        print("Result: Both files have the same size.")
    else:
        print("Result: Semantic JSON is larger than the image.")

    print(f"\nInference time: {inference_time:.2f} seconds")
    print(f"Output saved at: {OUTPUT_PATH}")

    print("\nStep 5: Completed successfully.")

except requests.exceptions.Timeout:
    print("\nERROR: Qwen took longer than 600 seconds.")
    print("Let the laptop cool before trying again.")

except requests.exceptions.ConnectionError:
    print("\nERROR: Cannot connect to Ollama.")
    print("Ensure the Ollama application is running.")

except requests.exceptions.RequestException as error:
    print(f"\nERROR: Ollama request failed: {error}")

except (OSError, ValueError) as error:
    print(f"\nERROR: Could not save or process results: {error}")
