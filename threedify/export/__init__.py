"""Export modules for 3Dify.
This module provides functionality for exporting 3D models to various formats.
"""
from typing import Dict
from threedify.export.base import BaseExporter
from threedify.export.gltf import GLTFExporter
from threedify.export.citygml import CityGMLExporter
from threedify.export.obj import OBJExporter
from threedify.export.ply import PLYExporter

_EXPORTERS: Dict[str, BaseExporter] = {
    "gltf": GLTFExporter(),
    "citygml": CityGMLExporter(),
    "obj": OBJExporter(),
    "ply": PLYExporter(),
}

def get_exporter(export_format: str) -> BaseExporter:
    """Get an exporter instance by format.
    Args:
        export_format (str): Type of exporter to get 
    Returns:
        BaseExporter: Exporter instance
    Raises:
        ValueError: If the exporter format is not registered
    """
    if export_format not in _EXPORTERS:
        raise ValueError(f"Unknown export format: {export_format}. "
                         f"Available formats: {list(_EXPORTERS.keys())}")
    return _EXPORTERS[export_format]

def register_exporter(export_format: str, exporter_instance: BaseExporter):
    """Register a new exporter format.
    Args:
        export_format (str): Format name to register
        exporter_instance (BaseExporter): Exporter instance to register  
    Returns:
        None
    """
    _EXPORTERS[export_format] = exporter_instance

__all__ = [
    "get_exporter", "register_exporter", "BaseExporter",
    "GLTFExporter", "CityGMLExporter", "OBJExporter", "PLYExporter"
]
