"""
VGGSounder Labels module for accessing video classification data.
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class VideoData:
    """
    Container for video data including labels and metadata.

    Attributes:
        video_id: The unique identifier for the video
        labels: List of classification labels for the video
        meta_labels: Dictionary containing metadata like background_music, static_image, voice_over
        modalities: List of modalities for each label (A, AV, V)
    """

    video_id: str
    labels: List[str]
    meta_labels: Dict[str, bool]
    modalities: List[str]

    def __repr__(self):
        return f"VideoData(video_id='{self.video_id}', labels={len(self.labels)} items, meta_labels={self.meta_labels})"


class VGGSounder:
    """
    Main interface for accessing VGGSounder video classification data.

    Provides dict-like access to video data by video ID.

    Example:
        >>> vggsounder = VGGSounder()
        >>> video_data = vggsounder["--U7joUcTCo_000000"]
        >>> print(video_data.labels)
        >>> print(video_data.meta_labels)
    """

    def __init__(self, csv_path: Optional[Union[str, Path]] = None):
        """
        Initialize the Labels object.

        Args:
            csv_path: Path to the CSV file. If None, looks for the default CSV file
                     in the package data directory.
        """
        self._data: Dict[str, VideoData] = {}
        self._csv_path = self._resolve_csv_path(csv_path)
        self._load_data()

    def _resolve_csv_path(self, csv_path: Optional[Union[str, Path]]) -> Path:
        """Resolve the path to the CSV file."""
        if csv_path is not None:
            return Path(csv_path)

        # Look for the CSV file in the package data directory first
        package_dir = Path(__file__).parent
        package_data_csv = package_dir / "data" / "vggsounder.csv"

        if package_data_csv.exists():
            return package_data_csv

        # Look for the CSV file in the project data directory (for development)
        project_data_csv = package_dir.parent / "data" / "vggsounder.csv"
        if project_data_csv.exists():
            return project_data_csv

        # If not found, look in common locations
        possible_paths = [
            Path("data/vggsounder.csv"),
            Path("../data/vggsounder.csv"),
            Path("vggsounder.csv"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        raise FileNotFoundError(
            f"Could not find vggsounder.csv. Please provide the path explicitly or "
            f"ensure the CSV file exists at one of these locations: {[str(p) for p in possible_paths + [str(package_data_csv), str(project_data_csv)]]}"
        )

    def _load_data(self):
        """Load data from the CSV file."""
        if not self._csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self._csv_path}")

        # Dictionary to group rows by video_id
        video_groups: Dict[str, List[Dict[str, str]]] = {}

        with open(self._csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                video_id = row["video_id"]
                if video_id not in video_groups:
                    video_groups[video_id] = []
                video_groups[video_id].append(row)

        # Process each video group
        for video_id, rows in video_groups.items():
            labels = []
            modalities = []

            # Extract labels and modalities
            for row in rows:
                labels.append(row["label"])
                modalities.append(row["modality"])

            # Extract metadata from the first row (should be consistent across all rows for same video)
            first_row = rows[0]
            meta_labels = {
                "background_music": first_row["background_music"].lower() == "true",
                "static_image": first_row["static_image"].lower() == "true",
                "voice_over": first_row["voice_over"].lower() == "true",
            }

            # Create VideoData object
            self._data[video_id] = VideoData(
                video_id=video_id,
                labels=labels,
                meta_labels=meta_labels,
                modalities=modalities,
            )

    def __getitem__(self, video_id: str) -> VideoData:
        """Get video data by video ID."""
        if video_id not in self._data:
            raise KeyError(f"Video ID '{video_id}' not found in dataset")
        return self._data[video_id]

    def __contains__(self, video_id: str) -> bool:
        """Check if video ID exists in dataset."""
        return video_id in self._data

    def __len__(self) -> int:
        """Return number of unique videos in dataset."""
        return len(self._data)

    def __iter__(self):
        """Iterate over video IDs."""
        return iter(self._data)

    def keys(self):
        """Return video IDs."""
        return self._data.keys()

    def values(self):
        """Return VideoData objects."""
        return self._data.values()

    def items(self):
        """Return (video_id, VideoData) pairs."""
        return self._data.items()

    def get_videos_with_labels(self, *label_names: str) -> List[VideoData]:
        """
        Get all videos that contain any of the specified labels.

        Args:
            *label_names: Label names to search for

        Returns:
            List of VideoData objects containing any of the specified labels
        """
        result = []
        for video_data in self._data.values():
            if any(label in video_data.labels for label in label_names):
                result.append(video_data)
        return result

    def get_videos_with_meta(self, **meta_filters) -> List[VideoData]:
        """
        Get all videos that match the specified metadata filters.

        Args:
            **meta_filters: Metadata filters (e.g., background_music=True)

        Returns:
            List of VideoData objects matching the metadata filters
        """
        result = []
        for video_data in self._data.values():
            if all(
                video_data.meta_labels.get(key) == value
                for key, value in meta_filters.items()
            ):
                result.append(video_data)
        return result

    def get_all_labels(self) -> List[str]:
        """Get all unique labels in the dataset."""
        all_labels = set()
        for video_data in self._data.values():
            all_labels.update(video_data.labels)
        return sorted(list(all_labels))

    def stats(self) -> Dict[str, int]:
        """Get basic statistics about the dataset."""
        total_videos = len(self._data)
        total_labels = sum(len(video_data.labels) for video_data in self._data.values())
        unique_labels = len(self.get_all_labels())

        with_background_music = len(self.get_videos_with_meta(background_music=True))
        with_static_image = len(self.get_videos_with_meta(static_image=True))
        with_voice_over = len(self.get_videos_with_meta(voice_over=True))

        return {
            "total_videos": total_videos,
            "total_label_instances": total_labels,
            "unique_labels": unique_labels,
            "videos_with_background_music": with_background_music,
            "videos_with_static_image": with_static_image,
            "videos_with_voice_over": with_voice_over,
        }
