"""Base processor interface for 3dify.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseProcessor(ABC):
    """Base class for data processors."""
    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any:
        """Process input data.
        Args:
            data: Input data
            **kwargs: Additional processor-specific parameters  
        Returns:
            Processed data
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the processor.
        Returns:
            str: Processor name
        """
        pass