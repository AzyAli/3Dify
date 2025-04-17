"""Data loaders for various input formats.
"""

import os
import logging
from typing import Dict, Union, Optional, Any
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class BaseLoader:
    """Base class for data loaders."""
    def __init__(self):
        """Initialize the loader."""
        pass
    
    def load(self, path: Union[str, Path], **kwargs) -> Any:
        """Load data from the given path.
        Args:
            path (str or Path): Path to the data file
            **kwargs: Additional loader-specific parameters  
        Returns:
            Loaded data
        """
        raise NotImplementedError("Subclasses must implement load()")
    
    @property
    def name(self) -> str:
        """Get the name of the loader.
        Returns:
            str: Loader name
        """
        raise NotImplementedError("Subclasses must implement name property")

class LidarLoader(BaseLoader):
    """Loader for LiDAR data (LAS/LAZ files)."""
    def load(self, path: Union[str, Path], **kwargs) -> Any:
        """Load LiDAR data from a LAS/LAZ file.
        Args:
            path (str or Path): Path to the LAS/LAZ file
            **kwargs: Additional loader-specific parameters   
        Returns:
            Loaded LiDAR data
        """
        import laspy
        logger.info(f"Loading LiDAR data from {path}")
    
        try:
            las_file = laspy.read(path)
            point_cloud = np.vstack((las_file.x, las_file.y, las_file.z)).transpose()

            if hasattr(las_file, 'red') and hasattr(las_file, 'green') and hasattr(las_file, 'blue'):
                colors = np.vstack((las_file.red, las_file.green, las_file.blue)).transpose()
                colors = colors / np.max(colors)
            else:
                colors = np.ones((point_cloud.shape[0], 3)) * 0.7
            if hasattr(las_file, 'intensity'):
                intensity = las_file.intensity
                intensity = intensity / np.max(intensity)
            else:
                intensity = np.ones(point_cloud.shape[0])
            
            if hasattr(las_file, 'classification'):
                classification = las_file.classification
            else:
                classification = np.zeros(point_cloud.shape[0], dtype=np.int32)
            result = type('LidarData', (), {
                'point_cloud': point_cloud,
                'colors': colors,
                'intensity': intensity,
                'classification': classification,
                'header': las_file.header,
                'path': path,
                'type': 'lidar'
            }) 
            logger.info(f"Loaded LiDAR data with {point_cloud.shape[0]} points")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load LiDAR data: {str(e)}")
            raise
    
    @property
    def name(self) -> str:
        """Get the name of the loader.
        Returns:
            str: Loader name
        """
        return "lidar"

class ImageLoader(BaseLoader):
    """Loader for image data (satellite, aerial, etc.)."""
    def load(self, path: Union[str, Path], **kwargs) -> Any:
        """Load image data from a file. 
        Args:
            path (str or Path): Path to the image file
            **kwargs: Additional loader-specific parameters 
        Returns:
            Loaded image data
        """
        from PIL import Image
        import numpy as np
        logger.info(f"Loading image data from {path}")
        try:
            img = Image.open(path)
            img_array = np.array(img)
            metadata = {
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format
            }
            result = type('ImageData', (), {
                'image': img,
                'array': img_array,
                'metadata': metadata,
                'path': path,
                'type': 'image'
            })
            
            logger.info(f"Loaded image data with dimensions {img.width}x{img.height}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load image data: {str(e)}")
            raise
    
    @property
    def name(self) -> str:
        """Get the name of the loader.
        Returns:
            str: Loader name
        """
        return "image"

class VectorLoader(BaseLoader):
    """Loader for vector data (SHP files)."""
    def load(self, path: Union[str, Path], **kwargs) -> Any:
        """Load vector data from a file.
        Args:
            path (str or Path): Path to the vector file
            **kwargs: Additional loader-specific parameters 
        Returns:
            Loaded vector data
        """
        try:
            logger.info(f"Loading vector data from {path}")
            vector_data = {"type": "vector", "path": str(path)}
            result = type('VectorData', (), {
                'vector': vector_data,
                'path': path,
                'type': 'vector'
            })
            logger.info(f"Loaded vector data")
            return result
        except Exception as e:
            logger.error(f"Failed to load vector data: {str(e)}")
            raise
    
    @property
    def name(self) -> str:
        """Get the name of the loader.
        Returns:
            str: Loader name
        """
        return "vector"

class TabularLoader(BaseLoader):
    """Loader for tabular data (CSV, etc.)."""
    def load(self, path: Union[str, Path], **kwargs) -> Any:
        """Load tabular data from a file.
        Args:
            path (str or Path): Path to the tabular file
            **kwargs: Additional loader-specific parameters
        Returns:
            Loaded tabular data
        """
        import pandas as pd
        logger.info(f"Loading tabular data from {path}")
        try:
            df = pd.read_csv(path, **kwargs)
            result = type('TabularData', (), {
                'dataframe': df,
                'path': path,
                'type': 'tabular'
            })
            logger.info(f"Loaded tabular data with {len(df)} rows and {len(df.columns)} columns")
            return result
        except Exception as e:
            logger.error(f"Failed to load tabular data: {str(e)}")
            raise
    
    @property
    def name(self) -> str:
        """Get the name of the loader.
        Returns:
            str: Loader name
        """
        return "tabular"

_LOADERS: Dict[str, BaseLoader] = {
    "lidar": LidarLoader(),
    "raster": ImageLoader(),
    "vector": VectorLoader(),
    "tabular": TabularLoader(),
}

def get_loader(loader_type: str) -> BaseLoader:
    """Get a loader instance by type.
    Args:
        loader_type (str): Type of loader to get  
    Returns:
        BaseLoader: Loader instance 
    Raises:
        ValueError: If the loader type is not registered
    """
    if loader_type not in _LOADERS:
        raise ValueError(f"Unknown loader type: {loader_type}. "
                         f"Available types: {list(_LOADERS.keys())}")
    return _LOADERS[loader_type]

def register_loader(loader_type: str, loader_instance: BaseLoader):
    """Register a new loader type.
    Args:
        loader_type (str): Type name to register
        loader_instance (BaseLoader): Loader instance to register 
    Returns:
        None
    """
    _LOADERS[loader_type] = loader_instance

def load_example(example_name: str) -> Any:
    """Load an example dataset.
    Args:
        example_name (str): Name of the example to load 
    Returns:
        Example data
    """
    logger.info(f"Loading example dataset: {example_name}")
    if example_name == "sample_lidar":
        # Create sample point cloud
        n_points = 1000
        point_cloud = np.random.randn(n_points, 3)
        colors = np.random.rand(n_points, 3)
        intensity = np.random.rand(n_points)
        classification = np.zeros(n_points, dtype=np.int32)
        
        result = type('LidarData', (), {
            'point_cloud': point_cloud,
            'colors': colors,
            'intensity': intensity,
            'classification': classification,
            'header': None,
            'path': None,
            'type': 'lidar'
        })
        return result
    
    elif example_name == "sample_image":
        from PIL import Image
        import numpy as np
        size = 256
        img = Image.new('RGB', (size, size), color='white')
        pixels = img.load()
        for i in range(size):
            for j in range(size):
                if (i // 32 + j // 32) % 2 == 0:
                    pixels[i, j] = (0, 0, 0)
        img_array = np.array(img)
        metadata = {
            'width': size,
            'height': size,
            'mode': 'RGB',
            'format': None
        }
        result = type('ImageData', (), {
            'image': img,
            'array': img_array,
            'metadata': metadata,
            'path': None,
            'type': 'image'
        })
        return result
    
    else:
        raise ValueError(f"Unknown example dataset: {example_name}")
