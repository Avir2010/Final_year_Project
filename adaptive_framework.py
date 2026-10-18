
from pathlib import Path

PROJECT_DIR = Path(r"D:\Final_Year_Project")
IMAGE_DIR = PROJECT_DIR / "Images"
RESULTS_DIR = PROJECT_DIR / "results"
ADAPTIVE_DIR = RESULTS_DIR / "adaptive_output"

MODES = ["auto", "image", "semantic", "hybrid"]


def choose_mode(
    bandwidth,
    visual_quality,
    need_semantics,
    manual_mode="auto"
):
    """
    Select a transmission mode.

    bandwidth: "low", "medium", or "high"
    visual_quality: "high" or "normal"
    need_semantics: True or False
    manual_mode: "auto", "image", "semantic", or "hybrid"
    """

    if manual_mode not in MODES:
        raise ValueError(
            f"Invalid mode. Choose one of: {MODES}"
        )

    # Manual override takes priority.
    if manual_mode != "auto":
        return manual_mode

    # Automatic selection rules.
    if visual_quality == "high":
        return "image"

    if need_semantics and bandwidth == "low":
        return "semantic"

    if need_semantics:
        return "hybrid"

    return "image"


if __name__ == "__main__":
    print("Adaptive Image Representation Framework")
    print("-" * 42)

    bandwidth = input(
        "Bandwidth (low/medium/high): "
    ).strip().lower()

    visual_quality = input(
        "Visual quality (high/normal): "
    ).strip().lower()

    semantics_input = input(
        "Is scene understanding required? (yes/no): "
    ).strip().lower()

    manual_mode = input(
        "Manual mode (auto/image/semantic/hybrid): "
    ).strip().lower()

    if bandwidth not in {"low", "medium", "high"}:
        raise ValueError("Invalid bandwidth selection.")

    if visual_quality not in {"high", "normal"}:
        raise ValueError("Invalid visual quality selection.")

    if semantics_input not in {"yes", "no"}:
        raise ValueError("Enter yes or no.")

    need_semantics = semantics_input == "yes"

    selected_mode = choose_mode(
        bandwidth=bandwidth,
        visual_quality=visual_quality,
        need_semantics=need_semantics,
        manual_mode=manual_mode
    )

    print(f"\nSelected transmission mode: {selected_mode}")
    print("Decision completed.")
    print("Next: connect the selected mode to its encoder.")
