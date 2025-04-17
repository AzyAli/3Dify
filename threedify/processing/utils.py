from typing import Dict
from threedify.processing.base import BaseProcessor
from threedify.processing.point_cloud import PointCloudProcessor
from threedify.processing.raster import RasterProcessor
from threedify.processing.vector import VectorProcessor
from threedify.processing.general import GeneralProcessor

_PROCESSORS: Dict[str, BaseProcessor] = {
    "point_cloud": PointCloudProcessor(),
    "raster": RasterProcessor(),
    "vector": VectorProcessor(),
    "general": GeneralProcessor(),
}

def get_processor(processor_type: str) -> BaseProcessor:
    """Get a processor instance by type.
    Args:
        processor_type (str): Type of processor to get
    Returns:
        BaseProcessor: Processor instance
    Raises:
        ValueError: If the processor type is not registered
    """
    if processor_type not in _PROCESSORS:
        raise ValueError(f"Unknown processor type: {processor_type}. "
                         f"Available types: {list(_PROCESSORS.keys())}")
    return _PROCESSORS[processor_type]

def register_processor(processor_type: str, processor_instance: BaseProcessor):
    """Register a new processor type.
    Args:
        processor_type (str): Type name to register
        processor_instance (BaseProcessor): Processor instance to register
    Returns:
        None
    """
    _PROCESSORS[processor_type] = processor_instance