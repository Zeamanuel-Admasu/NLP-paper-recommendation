# backend/scripts/download_models.py
from __future__ import annotations

import sys
import zipfile
import urllib.request
from pathlib import Path

MODELS_URL = "https://github.com/Zeamanuel-Admasu/NLP-paper-recommendation/releases/download/models-v1/models.zip"

def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading:\n  {url}\nTo:\n  {dest}")
    urllib.request.urlretrieve(url, dest)  # simple + works on Windows

def extract_zip(zip_path: Path, out_dir: Path) -> None:
    print(f"Extracting:\n  {zip_path}\nTo:\n  {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)

def main() -> int:
    backend_dir = Path(__file__).resolve().parents[1]      # backend/
    models_dir = backend_dir / "models"                   # backend/models/
    zip_path = backend_dir / "models.zip"                 # backend/models.zip (temporary)

    # If already present, skip
    expected_pb = models_dir / "full_model_savedmodel" / "saved_model.pb"
    if expected_pb.exists():
        print("Models already exist. Nothing to do.")
        return 0

    download_file(MODELS_URL, zip_path)
    extract_zip(zip_path, models_dir)

    # Some zips contain an extra top folder. If so, try to fix automatically.
    # We want: backend/models/full_model_savedmodel/saved_model.pb
    pb_here = models_dir / "full_model_savedmodel" / "saved_model.pb"
    if not pb_here.exists():
        # look for nested full_model_savedmodel
        candidates = list(models_dir.rglob("full_model_savedmodel/saved_model.pb"))
        if candidates:
            nested_pb = candidates[0]
            nested_root = nested_pb.parent.parent  # .../full_model_savedmodel
            target_root = models_dir / "full_model_savedmodel"
            print(f"Found nested model at: {nested_root}")
            print(f"Moving it to:        {target_root}")

            # Move folder contents
            target_root.parent.mkdir(parents=True, exist_ok=True)
            if target_root.exists():
                # if it exists, remove to avoid mixing
                import shutil
                shutil.rmtree(target_root)

            nested_root.rename(target_root)

    if not (models_dir / "full_model_savedmodel" / "saved_model.pb").exists():
        print("ERROR: saved_model.pb not found after extraction.")
        print("Check the zip contents and folder structure.")
        return 1

    # Optional: delete the zip after extraction
    try:
        zip_path.unlink(missing_ok=True)
    except Exception:
        pass

    print("Done. Models are ready.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
