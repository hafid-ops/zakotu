import os
import requests
import zipfile

#Config,
url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
save_dir = "data/models"
zip_path = os.path.join(save_dir, "vosk-model-small-en-us-0.15.zip")
extract_dir = os.path.join(save_dir, "vosk-model-small-en-us-0.15")

#Make sure save directory exists,
os.makedirs(save_dir, exist_ok=True)

#Skip if already extracted,
if os.path.exists(extract_dir):
    print(f" Model already exists at {extract_dir}")
else:
    print(" Downloading model...")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(zip_path, "wb") as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    done = int(50 * downloaded / total) if total else 0
                    print(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded//1024} KB", end="")
    print("\n Download complete:", zip_path)

    # Extract zip
    print(" Extracting...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(save_dir)
    print(" Extracted to:", extract_dir)

    # Remove zip file
    os.remove(zip_path)
    print(" Removed zip file.")