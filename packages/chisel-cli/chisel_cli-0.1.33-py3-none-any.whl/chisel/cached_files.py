"""
Cached files API client for Chisel.
Handles communication with the backend for large file caching.
"""

import os
import hashlib
import tempfile
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import requests

from .constants import CHISEL_BACKEND_URL, CHISEL_BACKEND_URL_ENV_KEY

# Minimum file size for caching (1GB)
MIN_CACHE_FILE_SIZE = 1 * 1024 * 1024 * 1024


class CachedFilesClient:
    """Client for interacting with the cached files API."""

    def __init__(self, api_key: str):
        """Initialize the cached files client."""
        self.api_key = api_key
        self.backend_url = os.environ.get(CHISEL_BACKEND_URL_ENV_KEY) or CHISEL_BACKEND_URL
        self.base_url = f"{self.backend_url}/api/v1/cached-files"

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def check_file_hash(self, file_hash: str) -> Dict[str, Any]:
        """
        Check if a file with the given hash exists in the cache.

        Returns:
            dict: Response with 'exists' boolean and optional 'file_info'
        """
        try:
            response = requests.post(
                f"{self.base_url}/check-hash",
                headers=self._get_headers(),
                data={"file_hash": file_hash},
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error checking file hash: {e}")
            return {"exists": False}

    def upload_cached_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Upload a file to the cache.

        Returns:
            dict: Response with upload result or None if failed
        """
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                response = requests.post(
                    f"{self.base_url}/upload", headers=self._get_headers(), files=files
                )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error uploading cached file: {e}")
            return None

    def increment_file_reference(self, file_id: str) -> bool:
        """
        Increment the reference count for a cached file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/{file_id}/increment-reference", headers=self._get_headers()
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error incrementing file reference: {e}")
            return False

    def decrement_file_reference(self, file_id: str) -> bool:
        """
        Decrement the reference count for a cached file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/{file_id}/decrement-reference", headers=self._get_headers()
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error decrementing file reference: {e}")
            return False


def scan_directory_for_large_files(
    directory: Path, min_size: int = MIN_CACHE_FILE_SIZE
) -> List[Path]:
    """
    Scan a directory for files larger than the minimum cache size.

    Args:
        directory: Directory to scan
        min_size: Minimum file size in bytes

    Returns:
        List of file paths that are larger than min_size
    """
    large_files = []
    print(f"Scanning directory: {directory}")
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                if file_path.stat().st_size >= min_size:
                    large_files.append(file_path)
            except (OSError, IOError):
                print(f"Error accessing file: {file_path}")
                # Skip files we can't access
                continue

    return large_files


def create_cached_file_placeholder(
    original_path: Path, cached_file_info: Dict[str, Any], relative_to: Path
) -> str:
    """
    Create a placeholder file content for a cached file.

    Args:
        original_path: Original file path
        cached_file_info: Information about the cached file from the API
        relative_to: Path to make the original_path relative to

    Returns:
        JSON string content for the placeholder
    """
    try:
        relative_path = original_path.relative_to(relative_to)
    except ValueError:
        relative_path = original_path

    placeholder_data = {
        "type": "keysandcaches_cached_file_link",
        "version": "1.0",
        "original_path": str(relative_path),
        "cached_file": {
            "id": cached_file_info["file_info"]["id"],
            "hash": cached_file_info["file_info"]["file_hash"],
            "filename": cached_file_info["file_info"]["original_filename"],
            "size": cached_file_info["file_info"]["file_size"],
        },
        "metadata": {
            "created_by": "chisel",
            "cache_date": cached_file_info["file_info"]["upload_date"],
        },
    }

    return json.dumps(placeholder_data, indent=2)


def is_cached_file_placeholder(file_path: Path) -> bool:
    """
    Check if a file is a cached file placeholder.

    Args:
        file_path: Path to the file to check

    Returns:
        True if it's a placeholder, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
            return data.get("type") == "keysandcaches_cached_file_link"
    except (IOError, json.JSONDecodeError, UnicodeDecodeError):
        return False


def parse_cached_file_placeholder(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse a cached file placeholder.

    Args:
        file_path: Path to the placeholder file

    Returns:
        Placeholder data if valid, None otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
            if data.get("type") == "keysandcaches_cached_file_link":
                return data
            return None
    except (IOError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def process_directory_for_cached_files(
    directory: Path, api_key: str, temp_dir: Optional[Path] = None
) -> Tuple[Path, List[Dict[str, Any]]]:
    """
    Process a directory to replace large files with cached file placeholders.

    Args:
        directory: Directory to process
        api_key: API key for authentication
        temp_dir: Temporary directory to create the processed directory in

    Returns:
        Tuple of (processed_directory_path, list_of_cached_file_references)
    """
    if temp_dir is None:
        temp_dir = Path(tempfile.mkdtemp())

    # Create a copy of the directory
    print(f"Processing directory: {directory}")
    processed_dir = temp_dir / directory.name
    print(f"Processed directory: {processed_dir}")

    # Remove existing directory if it exists to avoid conflicts
    if processed_dir.exists():
        print(f"Removing existing processed directory: {processed_dir}")
        shutil.rmtree(processed_dir)

    shutil.copytree(directory, processed_dir)

    # Initialize the cached files client
    client = CachedFilesClient(api_key)
    cached_files = []

    # Find large files in the processed directory
    large_files = scan_directory_for_large_files(processed_dir)
    print(f"Large files: {large_files}")
    if not large_files:
        return processed_dir, cached_files

    print(f"Found {len(large_files)} large file(s) to check for caching...")

    for file_path in large_files:
        try:
            # Calculate hash and check if it exists in cache
            file_hash = client.calculate_file_hash(file_path)
            check_result = client.check_file_hash(file_hash)
            print(f"Check result: {check_result} with file hash {file_hash}")

            if check_result.get("exists", False):
                # File exists in cache, create placeholder
                print(f"Using cached version of {file_path.name}")

                # Increment reference count
                file_id = check_result["file_info"]["id"]
                client.increment_file_reference(file_id)

                # Create placeholder content
                placeholder_content = create_cached_file_placeholder(
                    file_path, check_result, processed_dir
                )

                # Replace the file with placeholder
                placeholder_path = file_path.with_suffix(file_path.suffix + ".cached")
                with open(placeholder_path, "w", encoding="utf-8") as f:
                    f.write(placeholder_content)

                # Remove the original large file
                file_path.unlink()

                # Track the cached file reference
                cached_files.append(
                    {
                        "original_path": str(file_path.relative_to(processed_dir)),
                        "placeholder_path": str(placeholder_path.relative_to(processed_dir)),
                        "cached_file_id": file_id,
                        "file_hash": file_hash,
                    }
                )

            else:
                # File doesn't exist in cache, upload it
                print(f"Uploading {file_path.name} to cache...")

                upload_result = client.upload_cached_file(file_path)
                if upload_result and upload_result.get("success", False):
                    print(f"Successfully cached {file_path.name}")

                    # Create placeholder and replace file
                    check_result = {"file_info": upload_result["file_info"]}
                    placeholder_content = create_cached_file_placeholder(
                        file_path, check_result, processed_dir
                    )

                    placeholder_path = file_path.with_suffix(file_path.suffix + ".cached")
                    with open(placeholder_path, "w", encoding="utf-8") as f:
                        f.write(placeholder_content)

                    # Remove the original large file
                    file_path.unlink()

                    # Track the cached file reference
                    cached_files.append(
                        {
                            "original_path": str(file_path.relative_to(processed_dir)),
                            "placeholder_path": str(placeholder_path.relative_to(processed_dir)),
                            "cached_file_id": upload_result["file_info"]["id"],
                            "file_hash": file_hash,
                        }
                    )
                else:
                    print(f"Failed to upload {file_path.name} to cache, including in archive")

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            # Continue with the original file if processing fails
            continue

    return processed_dir, cached_files
