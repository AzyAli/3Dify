"""Base exporter interface for 3Dify.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from pathlib import Path

class BaseExporter(ABC):
    """Base class for 3D model exporters."""
    @abstractmethod
    def export(self, model_data: Any, output_path: Union[str, Path], **kwargs) -> Path:
        """Export model data to a file.
        Args:
            model_data: Model data to export
            output_path (str or Path): Path to save the output file
            **kwargs: Additional exporter-specific parameters 
        Returns:
            Path: Path to the exported file
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the exporter.
        Returns:
            str: Exporter name
        """
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        """Get the file extension for this exporter.
        Returns:
            str: File extension (without dot)
        """
        pass