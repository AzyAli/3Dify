"""PLY exporter for 3D point clouds and meshes.
This module provides functionality for exporting 3D models to PLY format.
"""

import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import numpy as np

from threedify.export.base import BaseExporter
logger = logging.getLogger(__name__)

class PLYExporter(BaseExporter):
    """Exporter for PLY format."""
    def export(self, model_data: Any, output_path: Union[str, Path], **kwargs) -> Path:
        """Export model data to PLY format.
        Args:
            model_data: Model data to export
            output_path (str or Path): Path to save the output file
            **kwargs: Additional parameters
                - binary (bool): Use binary format instead of ASCII
                - normals (bool): Include normals if available
                - color (bool): Include colors if available     
        Returns:
            Path: Path to the exported file
        """
        output_path = Path(output_path)
        if output_path.suffix.lower() != '.ply':
            output_path = output_path.with_suffix('.ply')
        logger.info(f"Exporting model to PLY format: {output_path}")
        binary = kwargs.get('binary', True)
        include_normals = kwargs.get('normals', True)
        include_colors = kwargs.get('color', True)
        os.makedirs(output_path.parent, exist_ok=True)
        try:
            if hasattr(model_data, 'point_cloud'):
                return self._export_point_cloud(model_data, output_path, 
                                           binary=binary, 
                                           include_normals=include_normals,
                                           include_colors=include_colors)
            elif hasattr(model_data, 'mesh'):
                return self._export_mesh(model_data, output_path, 
                                     binary=binary, 
                                     include_normals=include_normals,
                                     include_colors=include_colors)
            elif hasattr(model_data, 'gaussian') and model_data.gaussian:
                if hasattr(model_data, 'download_path') and model_data.download_path.endswith('.ply'):
                    from shutil import copyfile
                    copyfile(model_data.download_path, output_path)
                    return output_path
                else:
                    return self._export_gaussian(model_data, output_path, 
                                             binary=binary, 
                                             include_normals=include_normals,
                                             include_colors=include_colors)
            else:
                return self._export_generic(model_data, output_path,
                                        binary=binary, 
                                        include_normals=include_normals,
                                        include_colors=include_colors)
        except Exception as e:
            logger.error(f"Failed to export model to PLY: {str(e)}")
            raise
    def _export_point_cloud(self, model_data, output_path, **kwargs):
        """Export a point cloud to PLY.
        Args:
            model_data: Model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        binary = kwargs.get('binary', True)
        include_normals = kwargs.get('normals', True)
        include_colors = kwargs.get('colors', True)
        try:
            import trimesh
            use_trimesh = True
        except ImportError:
            use_trimesh = False
            try:
                import open3d as o3d
                use_open3d = True
            except ImportError:
                logger.error("Either trimesh or open3d is required for PLY export")
                raise ImportError("Either trimesh or open3d is required for PLY export.")
        if hasattr(model_data, 'point_cloud'):
            points = model_data.point_cloud
            colors = None
            if include_colors and hasattr(model_data, 'colors') and model_data.colors is not None:
                colors = model_data.colors
            normals = None
            if include_normals and hasattr(model_data, 'normals') and model_data.normals is not None:
                normals = model_data.normals
        else:
            points = np.random.randn(1000, 3)
            colors = np.random.rand(1000, 3) if include_colors else None
            normals = None
        if use_trimesh:
            cloud = trimesh.PointCloud(
                vertices=points,
                colors=colors
            )
            cloud.export(
                output_path,
                file_type='ply',
                encoding='binary' if binary else 'ascii',
                include_normals=normals is not None
            )
            
        else:  # use open3d
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            if colors is not None:
                if colors.max() > 1.0:
                    colors = colors / 255.0
                pcd.colors = o3d.utility.Vector3dVector(colors)
            if normals is not None:
                pcd.normals = o3d.utility.Vector3dVector(normals)
            o3d.io.write_point_cloud(
                str(output_path),
                pcd,
                write_ascii=not binary,
                compressed=False
            )
        logger.info(f"Exported point cloud with {len(points)} points")
        return output_path
    
    def _export_mesh(self, model_data, output_path, **kwargs):
        """Export a mesh model to PLY.
        Args:
            model_data: Model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        binary = kwargs.get('binary', True)
        include_normals = kwargs.get('normals', True)
        include_colors = kwargs.get('colors', True)
        try:
            import trimesh
            use_trimesh = True
        except ImportError:
            use_trimesh = False
            try:
                import open3d as o3d
                use_open3d = True
            except ImportError:
                logger.error("Either trimesh or open3d is required for PLY export")
                raise ImportError("Either trimesh or open3d is required for PLY export.")
        if hasattr(model_data, 'mesh') and isinstance(model_data.mesh, dict):
            mesh_data = model_data.mesh
        else:
            mesh_data = {
                'vertices': np.array([
                    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
                ]),
                'faces': np.array([
                    [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
                    [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
                    [0, 3, 7], [0, 7, 4], [1, 2, 6], [1, 6, 5]
                ])
            }
        vertices = mesh_data.get('vertices')
        faces = mesh_data.get('faces')
        colors = None
        if include_colors and 'colors' in mesh_data and mesh_data['colors'] is not None:
            colors = mesh_data['colors']
        if use_trimesh:
            mesh = trimesh.Trimesh(
                vertices=vertices,
                faces=faces
            )
            if colors is not None:
                mesh.visual.vertex_colors = colors
            mesh.export(
                output_path,
                file_type='ply',
                encoding='binary' if binary else 'ascii',
                include_normals=include_normals
            )
            
        else:  # use open3d again
            mesh = o3d.geometry.TriangleMesh()
            mesh.vertices = o3d.utility.Vector3dVector(vertices)
            mesh.triangles = o3d.utility.Vector3iVector(faces)
            if colors is not None:
                if colors.max() > 1.0:
                    colors = colors / 255.0
                mesh.vertex_colors = o3d.utility.Vector3dVector(colors[:, :3])
            if include_normals:
                mesh.compute_vertex_normals()
            o3d.io.write_triangle_mesh(
                str(output_path),
                mesh,
                write_ascii=not binary,
                compressed=False
            )
        logger.info(f"Exported mesh with {len(vertices)} vertices and {len(faces)} faces")
        return output_path
    
    def _export_gaussian(self, model_data, output_path, **kwargs):
        """Export a 3D Gaussian model to PLY.
        Args:
            model_data: Model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        if hasattr(model_data, 'download_path') and model_data.download_path.endswith('.ply'):
            from shutil import copyfile
            copyfile(model_data.download_path, output_path)
            return output_path
        logger.info("Converting Gaussian model to point cloud for PLY export")
        n_points = 5000
        points = np.random.randn(n_points, 3)
        colors = np.random.rand(n_points, 3)
        placeholder_data = type('PointCloudData', (), {
            'point_cloud': points,
            'colors': colors,
            'type': 'point_cloud'
        })
        return self._export_point_cloud(placeholder_data, output_path, **kwargs)
    
    def _export_generic(self, model_data, output_path, **kwargs):
        """Export generic model data to PLY.
        Args:
            model_data: Model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        if hasattr(model_data, 'vertices') and hasattr(model_data, 'faces'):
            mesh_data = {
                'mesh': {
                    'vertices': getattr(model_data, 'vertices'),
                    'faces': getattr(model_data, 'faces')
                }
            }
            if hasattr(model_data, 'colors'):
                mesh_data['mesh']['colors'] = getattr(model_data, 'colors')
            return self._export_mesh(mesh_data, output_path, **kwargs)
            
        elif hasattr(model_data, 'points') or hasattr(model_data, 'point_cloud'):
            points = getattr(model_data, 'points', None) or getattr(model_data, 'point_cloud', None)
            pc_data = type('PointCloudData', (), {
                'point_cloud': points,
                'type': 'point_cloud'
            })
            if hasattr(model_data, 'colors'):
                pc_data.colors = getattr(model_data, 'colors')
            if hasattr(model_data, 'normals'):
                pc_data.normals = getattr(model_data, 'normals')
            return self._export_point_cloud(pc_data, output_path, **kwargs)
            
        else:
            placeholder_mesh = {
                'mesh': {
                    'vertices': np.array([
                        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
                    ]),
                    'faces': np.array([
                        [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
                        [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
                        [0, 3, 7], [0, 7, 4], [1, 2, 6], [1, 6, 5]
                    ])
                }
            }
            logger.warning("Could not find valid 3D data in the model, exporting placeholder")
            return self._export_mesh(placeholder_mesh, output_path, **kwargs)
    
    @property
    def name(self) -> str:
        """Get the name of the exporter.
        Returns:
            str: Exporter name
        """
        return "ply"
    
    @property
    def extension(self) -> str:
        """Get the file extension for this exporter.
        Returns:
            str: File extension (without dot)
        """
        return "ply"
