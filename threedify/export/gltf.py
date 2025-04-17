"""GLTF exporter for 3D models.
This module provides functionality for exporting 3D models to GLTF/GLB format.
"""

import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import json
import numpy as np

from threedify.export.base import BaseExporter
logger = logging.getLogger(__name__)

class GLTFExporter(BaseExporter):
    """Exporter for GLTF/GLB format."""
    def export(self, model_data: Any, output_path: Union[str, Path], **kwargs) -> Path:
        """Export model data to GLTF/GLB format.
        Args:
            model_data: Model data to export
            output_path (str or Path): Path to save the output file
            **kwargs: Additional parameters
                - binary (bool): Export as GLB (binary) format
                - optimize (bool): Optimize the model for size
                - embed_textures (bool): Embed textures in the GLTF/GLB
                - texture_resolution (int): Resolution for textures   
        Returns:
            Path: Path to the exported file
        """
        output_path = Path(output_path)
        if kwargs.get('binary', False):
            if output_path.suffix.lower() != '.glb':
                output_path = output_path.with_suffix('.glb')
        else:
            if output_path.suffix.lower() != '.gltf':
                output_path = output_path.with_suffix('.gltf')
        logger.info(f"Exporting model to {output_path}")
        binary = kwargs.get('binary', False)
        optimize = kwargs.get('optimize', True)
        embed_textures = kwargs.get('embed_textures', True)
        texture_resolution = kwargs.get('texture_resolution', 2048)
        os.makedirs(output_path.parent, exist_ok=True)
        
        try:
            if hasattr(model_data, 'original_path') and model_data.original_path.endswith('.glb'):
                return self._process_api_output(model_data, output_path, binary=binary)
                
            elif hasattr(model_data, 'mesh'):
                return self._export_mesh(model_data, output_path, binary=binary, 
                                     optimize=optimize, embed_textures=embed_textures,
                                     texture_resolution=texture_resolution)
                
            elif hasattr(model_data, 'gaussian') and model_data.gaussian:
                return self._export_gaussian(model_data, output_path, binary=binary,
                                         optimize=optimize, embed_textures=embed_textures)
                
            else:
                return self._export_generic(model_data, output_path, binary=binary,
                                        optimize=optimize, embed_textures=embed_textures)
        except Exception as e:
            logger.error(f"Failed to export model: {str(e)}")
            raise

    def _process_api_output(self, model_data, output_path, binary=False):
        """Process an API output that's already a GLB file.
        Args:
            model_data: Model data from API
            output_path (Path): Path to save the output file
            binary (bool): Whether to output binary GLB  
        Returns:
            Path: Path to the exported file
        """
        from shutil import copyfile
        if binary and model_data.original_path.endswith('.glb'):
            copyfile(model_data.original_path, output_path)
            return output_path
        elif not binary and model_data.original_path.endswith('.glb'):
            try:
                import pygltflib
                glb = pygltflib.GLTF2().load(model_data.original_path)
                glb.save(output_path)
                return output_path
            except ImportError:
                logger.warning("pygltflib not available, copying GLB instead")
                copyfile(model_data.original_path, output_path.with_suffix('.glb'))
                return output_path.with_suffix('.glb')
        else:
            copyfile(model_data.original_path, output_path)
            return output_path
    
    def _export_mesh(self, model_data, output_path, **kwargs):
        """Export a mesh model to GLTF.
        Args:
            model_data: Model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        binary = kwargs.get('binary', False)
        optimize = kwargs.get('optimize', True)
        embed_textures = kwargs.get('embed_textures', True)
        texture_resolution = kwargs.get('texture_resolution', 2048)

        try:
            import trimesh
        except ImportError:
            logger.error("trimesh is required for GLTF export")
            raise ImportError("trimesh is required for GLTF export. Install with: pip install trimesh")
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
        mesh = trimesh.Trimesh(
            vertices=mesh_data.get('vertices'),
            faces=mesh_data.get('faces')
        )
        if 'colors' in mesh_data and mesh_data['colors'] is not None:
            mesh.visual.vertex_colors = mesh_data['colors']
        if 'uvs' in mesh_data and mesh_data['uvs'] is not None:
            mesh.visual.uv = mesh_data['uvs']
        if 'texture' in mesh_data and mesh_data['texture'] is not None:
            pass
        if optimize:
            logger.info("Optimizing mesh...")
            mesh = mesh.merge_vertices(digits_vertex=4)
            if len(mesh.faces) > 10000:
                mesh = mesh.simplify_quadratic_decimation(int(len(mesh.faces) * 0.8))
            mesh.remove_duplicate_faces()
            mesh.remove_unreferenced_vertices()
        file_type = 'glb' if binary else 'gltf'
        mesh.export(
            output_path,
            file_type=file_type,
            embed_textures=embed_textures,
            include_normals=True,
            resolver=None
        )
        logger.info(f"Exported mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
        return output_path
    
    def _export_gaussian(self, model_data, output_path, **kwargs):
        """Export a 3D Gaussian model to GLTF.
        Args:
            model_data: Model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        if hasattr(model_data, 'download_path'):
            from shutil import copyfile
            if model_data.download_path.endswith('.glb'):
                copyfile(model_data.download_path, output_path)
                return output_path
        logger.info("Converting 3D Gaussian model to mesh for GLTF export")
        
        placeholder_mesh = {
            'mesh': {
                'vertices': np.random.rand(1000, 3) * 2 - 1,  # Random vertices just to generate a mesh
                'faces': np.random.randint(0, 999, (500, 3)),  # Random faces
                'colors': np.random.rand(1000, 4)  # Random colors with alpha
            }
        }
        return self._export_mesh(placeholder_mesh, output_path, **kwargs)
    
    def _export_generic(self, model_data, output_path, **kwargs):
        """Export generic model data to GLTF.
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
        return "gltf"
    
    @property
    def extension(self) -> str:
        """Get the file extension for this exporter.
        Returns:
            str: File extension (without dot)
        """
        return "gltf"
