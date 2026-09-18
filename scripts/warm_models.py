from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from temuprivacyscreen.model_cache import configure_model_cache

cache_dir = configure_model_cache()
print(f"Model cache directory: {cache_dir}")

from uniface import MobileGaze, RetinaFace
from uniface.constants import GazeWeights, RetinaFaceWeights


def main() -> None:
    print("Downloading/verifying face detector weights (RetinaFace mnet_025)...")
    RetinaFace(model_name=RetinaFaceWeights.MNET_025)

    print("Downloading/verifying gaze estimator weights (MobileGaze mobileone_s0)...")
    MobileGaze(model_name=GazeWeights.MOBILEONE_S0)

    print("All models downloaded and verified inside the venv.")


if __name__ == "__main__":
    main()
