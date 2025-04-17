"""3dify: Spatial data tO 3D model generation for flood risk management
A comprehensive Python library for processing geospatial data (some LiDAR and satellite images)
into 3D models for flood risk analysis and digital twin applications.(or at least that's what i will try and do)
"""
__version__ = "0.1.0"

from threedify.core.pipeline import Pipeline
from threedify.visualization.jupyter import init_notebook

def create_pipeline(config=None, verbose=True):
    """Create a new processing pipeline with optional configuration.
    Args:
        config (dict, optional): Configuration parameters for the pipeline
        verbose (bool): Whether to display verbose output
    Returns:
        Pipeline: Configured processing pipeline
    """
    from threedify.core.pipeline import Pipeline
    return Pipeline(config=config, verbose=verbose)

def load_example_data(example_name="sample_lidar"):
    """Load example data for demonstration purposes.
    Args:
        example_name (str): Name of the example dataset to load
    Returns:
        object: Loaded example data
    """  
    from threedify.data.loaders import load_example
    return load_example(example_name)

__all__ = [
    "create_pipeline",
    "load_example_data",
    "Pipeline",
    "init_notebook"
]
