#!/usr/bin/env python3
"""
Zenodo dataset accessor.
"""

from abc import ABC, abstractmethod
import logging
import urllib.request
import json
import tempfile
from pathlib import Path

from tqdm import tqdm
from pypassist.mixin.registrable import Registrable

LOGGER = logging.getLogger(__name__)


class ZenodoAccessor(ABC, Registrable):
    """
    Zenodo dataset accessor.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "./type"

    _DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "zenodo_datasets"

    def __init__(self, record_id, filename, cache_dir=None):
        """
        Initialize ZenodoAccessor.

        Args:
            record_id (str): Zenodo record ID
            filename (str): Name of the file to download
            cache_dir (str, optional): Cache directory. Defaults to system temp directory
        """
        self._record_id = record_id
        self._filename = filename
        self._url = (
            f"https://zenodo.org/api/records/{record_id}/files/{filename}/content"
        )
        self._api_url = f"https://zenodo.org/api/records/{record_id}/files/{filename}"

        self._cache_dir = cache_dir
        self._expected_size = None

    @property
    def local_path(self):
        """Local path to the cached file."""
        return self.cache_dir / f"{self._filename}"

    @property
    def cache_dir(self):
        """Cache directory."""
        cache_dir = self._cache_dir
        if cache_dir is None:
            self._cache_dir = self._DEFAULT_CACHE_DIR

        self._cache_dir.mkdir(parents=True, exist_ok=True)
        return self._cache_dir

    @property
    def expected_size(self):
        """Get expected file size from Zenodo API."""
        if self._expected_size is not None:
            return self._expected_size

        with urllib.request.urlopen(self._api_url) as response:
            metadata = json.loads(response.read().decode("utf-8"))
            return metadata.get("size", 0)

    def _is_file_valid(self):
        """Check if cached file exists and has correct size."""
        if not self.local_path.exists():
            return False

        expected_size = self.expected_size
        if expected_size == 0:
            return True  # Skip validation if size unknown

        actual_size = self.local_path.stat().st_size
        return actual_size == expected_size

    def download(self, force=False):
        """
        Download file from Zenodo if not cached or invalid.

        Args:
            force (bool): Force download even if file exists

        Returns:
            Path: Path to the downloaded file
        """
        if not force and self._is_file_valid():
            LOGGER.info("Using cached file: %s", self.local_path)
            return self.local_path

        LOGGER.info("Downloading %s...", self._filename)

        with urllib.request.urlopen(self._url) as response:
            total_size = self.expected_size
            with tqdm(
                total=total_size, unit="B", unit_scale=True, desc=self._filename
            ) as pbar:
                with open(self.local_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))

        # Verify download
        if not self._is_file_valid():
            self.local_path.unlink()
            raise ValueError(
                f"Downloaded file size mismatch for {self._filename}. Please try again."
            )

        LOGGER.info("Downloaded to %s", self.local_path)
        return self.local_path

    def get(self, force=False):
        """
        Download and give access to data from Zenodo dataset.

        Args:
            force (bool): Force download even if file exists

        Returns:
            Data accessed by the implementation
        """
        self.download(force)
        return self._access_impl()

    @abstractmethod
    def _access_impl(self):
        """
        Implementation of the data access logic.

        Returns:
            Accessible data
        """

    @classmethod
    def init(cls, accessor_type, cache_dir=None):
        """
        Initialize a Zenodo accessor class dynamically.

        Args:
            accessor_type (str): Type of accessor to create
            cache_dir (str, optional): Cache directory. Defaults to system temp directory

        Returns:
            ZenodoAccessor: Instance of the requested accessor type
        """
        return cls.get_registered(accessor_type)(cache_dir=cache_dir)
