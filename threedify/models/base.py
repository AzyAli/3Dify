"""Base model interface for 3D generation models.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseModel(ABC):
    """Abstract base class for 3D generation models."""
    @abstractmethod
    def generate(self, data: Any, **kwargs) -> Any:
        """Generate a 3D model from input data.
        Args:
            data (Any): Input data for model
            **kwargs: Additional keyword arguments for the model
        Returns:
            Any: Generated 3D model
        """
        pass
    @abstractmethod
    def load_weights(self, weights_path: str):
        """Load model weights from a file.
        Args:
            weights_path (str): Path to the model weights file
        Returns:
            self: Model instance for method chaining
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the model.
        Returns:
            str: Name of the model
        """
        pass

