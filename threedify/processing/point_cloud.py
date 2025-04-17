"""
Point cloud processing module. In a real implementation, I would use a proper algorithm for the outliers and normals.
This is a simplified version for to just show as an example. Also, we can use libraries like Open3D or PCL for more advanced processing.
for processing the buildings we would Segment the building (roof, walls, etc.) and extract building features as well(well time did not allow for that).
"""

import logging
from typing import Any, Dict, Optional, List, Tuple, Union
import numpy as np

from threedify.processing.base import BaseProcessor
logger = logging.getLogger(__name__)

class PointCloudProcessor(BaseProcessor):
    """Processor for point cloud data."""
    def process(self, data: Any, **kwargs) -> Any:
        """Process point cloud data.
        Args:
            data: Input point cloud data
            **kwargs: Additional processor-specific parameters
                - downsample (float): Downsample factor (0.0-1.0)
                - remove_outliers (bool): Whether to remove outliers
                - estimate_normals (bool): Whether to estimate normals
                - building_mode (bool): Special processing for buildings    
        Returns:
            Processed point cloud data
        """
        logger.info("Processing point cloud data")

        if hasattr(data, 'point_cloud'):
            point_cloud = data.point_cloud
            colors = getattr(data, 'colors', None)
            intensity = getattr(data, 'intensity', None)
            classification = getattr(data, 'classification', None)
        else:
            point_cloud = data
            colors = None
            intensity = None
            classification = None
        downsample = kwargs.get('downsample', 1.0)
        remove_outliers = kwargs.get('remove_outliers', False)
        estimate_normals = kwargs.get('estimate_normals', True)
        building_mode = kwargs.get('building_mode', False)
        processed_point_cloud = point_cloud.copy()
        processed_colors = colors.copy() if colors is not None else None

        if downsample < 1.0:
            processed_point_cloud, processed_colors = self._downsample(
                processed_point_cloud, processed_colors, downsample)
 
        if remove_outliers:
            processed_point_cloud, processed_colors = self._remove_outliers(
                processed_point_cloud, processed_colors)

        if estimate_normals:
            normals = self._estimate_normals(processed_point_cloud)
        else:
            normals = None

        if building_mode:
            processed_point_cloud, processed_colors, building_segments = self._process_building(
                processed_point_cloud, processed_colors)
        else:
            building_segments = None

        processed_data = type('ProcessedPointCloud', (), {
            'point_cloud': processed_point_cloud,
            'colors': processed_colors,
            'normals': normals,
            'building_segments': building_segments,
            'original_data': data,
            'type': 'processed_point_cloud'
        })
        logger.info(f"Point cloud processing complete. Result has {len(processed_point_cloud)} points")
        return processed_data
    
    def _downsample(self, point_cloud: np.ndarray, colors: Optional[np.ndarray], 
                    factor: float) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Downsample a point cloud.
        Args:
            point_cloud (np.ndarray): Point cloud to downsample
            colors (np.ndarray): Colors of the point cloud
            factor (float): Downsample factor (0.0-1.0)
        Returns:
            tuple: Downsampled point cloud and colors
        """
        logger.info(f"Downsampling point cloud with factor {factor}")
        n_points = len(point_cloud)
        n_sample = max(1, int(n_points * factor))
        if n_sample >= n_points:
            return point_cloud, colors
        indices = np.random.choice(n_points, n_sample, replace=False)
        downsampled_point_cloud = point_cloud[indices]
        downsampled_colors = colors[indices] if colors is not None else None
        logger.info(f"Downsampled from {n_points} to {n_sample} points")
        return downsampled_point_cloud, downsampled_colors
    
    def _remove_outliers(self, point_cloud: np.ndarray, 
                          colors: Optional[np.ndarray]) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Remove outliers from a point cloud.
        Args:
            point_cloud (np.ndarray): Point cloud to process
            colors (np.ndarray): Colors of the point cloud   
        Returns:
            tuple: Processed point cloud and colors
        """
        logger.info("Removing outliers from point cloud")
        center = np.mean(point_cloud, axis=0)
        distances = np.linalg.norm(point_cloud - center, axis=1)
        threshold = np.mean(distances) + 2 * np.std(distances)
        mask = distances < threshold
        filtered_point_cloud = point_cloud[mask]
        filtered_colors = colors[mask] if colors is not None else None
        logger.info(f"Removed {np.sum(~mask)} outliers out of {len(point_cloud)} points")
        return filtered_point_cloud, filtered_colors
    
    def _estimate_normals(self, point_cloud: np.ndarray) -> np.ndarray:
        """Estimate normals for a point cloud.
        Args:
            point_cloud (np.ndarray): Point cloud to process   
        Returns:
            np.ndarray: Estimated normals
        """
        logger.info("Estimating normals for point cloud")
        normals = np.random.randn(*point_cloud.shape)
        normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)
        return normals
    
    def _process_building(self, point_cloud: np.ndarray, 
                          colors: Optional[np.ndarray]) -> Tuple[np.ndarray, Optional[np.ndarray], Dict]:
        """Apply specialized processing for buildings.
        Args:
            point_cloud (np.ndarray): Point cloud to process
            colors (np.ndarray): Colors of the point cloud
        Returns:
            tuple: Processed point cloud, colors, and building segments
        """
        logger.info("Applying specialized processing for buildings")
        building_segments = {
            'roof': {'indices': np.where(point_cloud[:, 2] > np.median(point_cloud[:, 2]))[0]},
            'walls': {'indices': np.where(point_cloud[:, 2] <= np.median(point_cloud[:, 2]))[0]},
        }
        return point_cloud, colors, building_segments
    
    @property
    def name(self) -> str:
        """Get the name of the processor.
        Returns:
            str: Processor name
        """
        return "point_cloud"
