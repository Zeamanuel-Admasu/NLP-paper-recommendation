from pathlib import Path
import os
import zipfile
import urllib.request

def main():
    project_root = Path(__file__).resolve().parents[2]   # arxiv-assistant/
    models_dir = project_root / "backend" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    zip_url = os.environ.get("MODELS_ZIP_URL")
    if not zip_url:
        raise SystemExit(
            "MODELS_ZIP_URL is not set.\n"
            "Example (PowerShell):\n"
            "$env:MODELS_ZIP_URL='https://.../models.zip'\n"
            "python backend/scripts/download_models.py"
        )

    zip_path = project_root / "models.zip"

    print("Downloading models.zip...")
    urllib.request.urlretrieve(zip_url, zip_path)

    print("Extracting into backend/models/ ...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(models_dir)

    zip_path.unlink(missing_ok=True)
    print("Done. Models are ready at:", models_dir)

if __name__ == "__main__":
    main()
