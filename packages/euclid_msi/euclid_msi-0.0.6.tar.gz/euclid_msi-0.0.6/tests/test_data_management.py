"""
Test script for data management functionality.
"""

import os
import shutil
from pathlib import Path
import requests
from tqdm import tqdm
import hashlib

# Define the data directory
DATA_DIR = Path(os.path.expanduser("~")) / ".euclid_msi" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Define required files and their expected locations
REQUIRED_FILES = {
    "structures.sdf": DATA_DIR / "structures.sdf",
    "HMDB_complete.csv": DATA_DIR / "HMDB_complete.csv",
    "lipidclasscolors.h5ad": DATA_DIR / "lipidclasscolors.h5ad"
}

# Zenodo record information
ZENODO_RECORD_ID = "15650014"
ZENODO_BASE_URL = f"https://zenodo.org/record/{ZENODO_RECORD_ID}/files"

# File checksums for verification
FILE_CHECKSUMS = {
    "structures.sdf": "e36a2d72c6f863c8047a6067ef2117ef",
    "HMDB_complete.csv": "34641c9fd3c25ea131a56103bfaf060b",
    "lipidclasscolors.h5ad": "d23ea9ea2fa081f9d843670283485e78"
}

def download_file(url: str, destination: Path) -> None:
    """Download a file from a URL with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f, tqdm(
        desc=destination.name,
        total=total_size,
        unit='iB',
        unit_scale=True
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def verify_file_checksum(filepath: Path, expected_checksum: str) -> bool:
    """Verify the MD5 checksum of a downloaded file."""
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    
    return md5_hash.hexdigest() == expected_checksum

def test_download_and_verify():
    """Test downloading and verifying a small file."""
    # Test with the smallest file first (lipidclasscolors.h5ad)
    filename = "lipidclasscolors.h5ad"
    filepath = REQUIRED_FILES[filename]
    expected_checksum = FILE_CHECKSUMS[filename]
    
    print(f"\nTesting download and verification of {filename}...")
    
    # Download the file
    url = f"{ZENODO_BASE_URL}/{filename}?download=1"
    try:
        download_file(url, filepath)
        print(f"Downloaded {filename}")
        
        # Verify checksum
        if verify_file_checksum(filepath, expected_checksum):
            print(f"Checksum verification passed for {filename}")
        else:
            print(f"Checksum verification failed for {filename}")
            if filepath.exists():
                filepath.unlink()
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        if filepath.exists():
            filepath.unlink()

if __name__ == "__main__":
    print("Starting data management test...")
    test_download_and_verify()