import os
import time
from nudenet import NudeDetector

# https://github.com/notAI-tech/NudeNet
# This uses an object detection model, not a classifier.
# It will download the detector model on first run.
# TODO: Check the following later and see their performance against this:
#  - openai/clip-vit-base-patch32
#  - laion/CLIP-based-NSFW-Detector
_detector = NudeDetector()

CRITICAL_LABELS = {
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
}

SUGGESTIVE_LABELS = {
    "FEMALE_BREAST_COVERED",
    "FEMALE_GENITALIA_COVERED",
    "MALE_GENITALIA_COVERED",
    "BELLY_EXPOSED",
    "BUTTOCKS_EXPOSED",
}

class NSFWGeneratedOutput(Exception):
    """Raised when an image is classified as NSFW."""
    pass

def check_nsfw(image_path: str, threshold: float = 0.7, block_suggestive: bool = True):
    """
    Run NSFW classification on a generated image.

    There are two tiers of detections:
      1. Critical exposures (nudity: genitals, exposed breasts, anus) → always blocked.
      2. Suggestive content (lingerie, bikinis, covered breasts/genitals, etc.) → 
         optionally blocked if `block_suggestive=True`.

    Why parameterized?
      Some prompts/themes (e.g. "KPop Idol") may trigger suggestive detections even
      when they're acceptable (clothed but revealing). To reduce false positives,
      we can disable suggestive blocking with `block_suggestive=False`.

      On the other hand, stricter styles (e.g. "Kimono", "Hanbok Princess") may
      require `block_suggestive=True` to ensure even borderline suggestive content
      is rejected.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    start = time.time()
    preds = _detector.detect(image_path)
    elapsed = time.time() - start

    print(f"🔎 {image_path}: detections={preds}")
    print(f"⏱️ NSFW detection took {elapsed:.3f} seconds")

    for pred in preds:
        label = pred.get("class", "UNKNOWN")
        score = pred.get("score", 0.0)

        # Critical exposures always blocked
        if label in CRITICAL_LABELS and score >= threshold:
            raise NSFWGeneratedOutput(
                f"[NSFW] {image_path} (label={label}, score={score:.2f})"
            )

        # Suggestive if you decide to block lingerie, bikinis, etc.
        if block_suggestive and label in SUGGESTIVE_LABELS and score >= threshold:
            raise NSFWGeneratedOutput(
                f"[NSFW-SUGGESTIVE] {image_path} (label={label}, score={score:.2f})"
            )

    return True