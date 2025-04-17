"""Base visualizer interface for threedify.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseVisualizer(ABC):
    """Base class for visualizers."""
    @abstractmethod
    def visualize(self, model_data: Any, **kwargs) -> Any:
        """Visualize model data.
        Args:
            model_data: Model data to visualize
            **kwargs: Additional visualizer-specific parameters 
        Returns:
            Visualization result
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the visualizer.
        Returns:
            str: Visualizer name
        """
        pass
