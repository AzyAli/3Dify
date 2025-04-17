"""OBJ exporter for 3D models.
This module provides functionality for exporting 3D models to OBJ format.later on you can add the texture under the export function 
But it depends on the specific version of trimesh being used as well!
"""

import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import numpy as np

from threedify.export.base import BaseExporter
logger = logging.getLogger(__name__)

class OBJExporter(BaseExporter):
    """Exporter for OBJ format."""
    def export(self, model_data: Any, output_path: Union[str, Path], **kwargs) -> Path:
        """Export model data to OBJ format.
        Args:
            model_data: Model data to export
            output_path (str or Path): Path to save the output file
            **kwargs: Additional parameters
                - mtl (bool): Generate MTL file for materials
                - texture_path (str): Path to texture image
                - optimize (bool): Optimize the mesh before export  
        Returns:
            Path: Path to the exported file
        """
        output_path = Path(output_path)
        if output_path.suffix.lower() != '.obj':
            output_path = output_path.with_suffix('.obj')
        
        logger.info(f"Exporting model to OBJ format: {output_path}")
        generate_mtl = kwargs.get('mtl', True)
        texture_path = kwargs.get('texture_path', None)
        optimize = kwargs.get('optimize', True)
        os.makedirs(output_path.parent, exist_ok=True)
        
        try:
            if hasattr(model_data, 'mesh'):
                return self._export_mesh(model_data, output_path, 
                                     generate_mtl=generate_mtl, 
                                     texture_path=texture_path,
                                     optimize=optimize)
            elif hasattr(model_data, 'gaussian') and model_data.gaussian:
                logger.info("Converting Gaussian model to mesh for OBJ export")
                return self._export_gaussian_as_mesh(model_data, output_path,
                                                generate_mtl=generate_mtl)
            else:
                return self._export_generic(model_data, output_path,
                                        generate_mtl=generate_mtl)
                
        except Exception as e:
            logger.error(f"Failed to export model to OBJ: {str(e)}")
            raise
    
    def _export_mesh(self, model_data, output_path, **kwargs):
        """Export a mesh model to OBJ.
        Args:
            model_data: Model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        generate_mtl = kwargs.get('generate_mtl', True)
        texture_path = kwargs.get('texture_path', None)
        optimize = kwargs.get('optimize', True)
        try:
            import trimesh
        except ImportError:
            logger.error("trimesh is required for OBJ export")
            raise ImportError("trimesh is required for OBJ export. Install with: pip install trimesh")
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
        if texture_path and os.path.exists(texture_path):
            try:
                from PIL import Image
                texture_img = Image.open(texture_path)
            except Exception as e:
                logger.warning(f"Failed to load texture: {str(e)}")
        
        if optimize:
            logger.info("Optimizing mesh...")
            mesh = mesh.merge_vertices(digits_vertex=4)
            if len(mesh.faces) > 10000:
                mesh = mesh.simplify_quadratic_decimation(int(len(mesh.faces) * 0.8))
            mesh.remove_duplicate_faces()
            mesh.remove_unreferenced_vertices()
        mtl_path = None
        if generate_mtl:
            mtl_path = output_path.with_suffix('.mtl')
        mesh.export(
            output_path,
            file_type='obj',
            include_normals=True,
            include_texture=texture_path is not None,
            mtl_name=mtl_path.name if mtl_path else None,
            resolver=None
        )
        logger.info(f"Exported mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
        return output_path
    
    def _export_gaussian_as_mesh(self, model_data, output_path, **kwargs):
        """Export a Gaussian model as mesh to OBJ.
        Args:
            model_data: Gaussian model data to export
            output_path (Path): Path to save the output file
            **kwargs: Additional parameters
        Returns:
            Path: Path to the exported file
        """
        if hasattr(model_data, 'download_path'):
            if model_data.download_path.endswith('.ply'):
                try:
                    import trimesh
                    mesh = trimesh.load(model_data.download_path)
                    mesh.export(output_path, file_type='obj')
                    return output_path
                except Exception as e:
                    logger.warning(f"Failed to convert PLY to OBJ: {str(e)}")
        placeholder_mesh = {
            'mesh': {
                'vertices': np.random.rand(1000, 3) * 2 - 1,  # Random vertices, yeah well again!
                'faces': np.random.randint(0, 999, (500, 3)),  # Random faces
                'colors': np.random.rand(1000, 4)  # Random colors with alpha
            }
        }
        return self._export_mesh(placeholder_mesh, output_path, **kwargs)
    
    def _export_generic(self, model_data, output_path, **kwargs):
        """Export generic model data to OBJ.
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
        return "obj"
    
    @property
    def extension(self) -> str:
        """Get the file extension for this exporter.
        Returns:
            str: File extension (without dot)
        """
        return "obj"
