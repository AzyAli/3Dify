"""Bolt3D model integration for 3D generation using Splatter Image API.
"""

import os
import logging
import tempfile
from typing import Any, Dict, Optional, Union, List, Tuple
from pathlib import Path
import time
import numpy as np
from PIL import Image

from threedify.models.base import BaseModel

try:
    from gradio_client import Client
except ImportError:
    raise ImportError(
        "gradio_client is required for API access to Bolt3D. "
        "Install it with: pip install gradio_client"
    )
logger = logging.getLogger(__name__)

class Bolt3DModel(BaseModel):
    """Bolt3D model for generating 3D models from images using the Splatter Image API.
    This model uses the Hugging Face hosted Splatter Image API to generate 3D models.
    """
    def __init__(self, api_url: str = "szymanowiczs/splatter_image"):
        """Initialize the Bolt3D model API client.
        Args:
            api_url (str): URL to the Splatter Image API (default uses the official HF space)
        """
        self._api_url = api_url
        self._client = None
    
    def generate(self, data: Any, **kwargs) -> Any:
        """Generate a 3D model from input data.
        Args:
            data: Input data (image)
            **kwargs: Additional parameters
                - preprocess_background (bool): Whether to remove the background from the image        
        Returns:
            Generated 3D model data
        """
        if self._client is None:
            self._connect_api()
        preprocessed_data = self._preprocess(data)
        logger.info("Validating input image")
        
        try:
            _ = self._client.predict(
                input_image=preprocessed_data,
                api_name="/check_input_image"
            )
            preprocess_background = kwargs.get('preprocess_background', True)
            logger.info(f"Preprocessing image (remove background: {preprocess_background})")
            processed_image = self._client.predict(
                input_image=preprocessed_data,
                preprocess_background=preprocess_background,
                api_name="/preprocess"
            )
            logger.info("Generating 3D model with Bolt3D API")
            model_path = self._client.predict(
                image=processed_image,
                api_name="/reconstruct_and_export"
            )
            processed_results = self._postprocess(model_path)
            return processed_results
            
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise
    
    def _connect_api(self):
        """Connect to the Bolt3D API.
        """
        logger.info(f"Connecting to Bolt3D API at {self._api_url}")

        # try:
        self._client = Client(self._api_url)
        logger.info("Connected to Bolt3D API successfully")
            
    
    def _preprocess(self, data):
        """Placeholder - Preprocess input data for Bolt3D.
        Args:
            data: Input data    
        Returns:
            Preprocessed data ready for Bolt3D API
        """
        return data
    
    def _postprocess(self, model_path):
        """Postprocess Bolt3D output.
        Args:
            model_path: Path to the generated model  
        Returns:
            Processed results in a standard format
        """
        if model_path.endswith('.glb'):
            import trimesh
            
            try:
                mesh = trimesh.load(model_path)
                vertices = np.array(mesh.vertices)
                faces = np.array(mesh.faces)
                mesh_data = {
                    'vertices': vertices,
                    'faces': faces
                }
                if hasattr(mesh.visual, 'material'):
                    if hasattr(mesh.visual.material, 'image'):
                        mesh_data['texture'] = mesh.visual.material.image
                if hasattr(mesh.visual, 'uv'):
                    mesh_data['uvs'] = mesh.visual.uv
                result = type('Bolt3DResult', (), {
                    'mesh': mesh_data,
                    'format': 'glb',
                    'original_path': model_path,
                    'type': 'bolt3d_result'
                })
                return result
                
            except Exception as e:
                logger.error(f"Failed to process Bolt3D output: {str(e)}")
                result = type('Bolt3DResult', (), {
                    'mesh': None,
                    'format': 'glb',
                    'original_path': model_path,
                    'type': 'bolt3d_result'
                })               
                return result
        else:
            # If it's not a GLB, just return the path
            result = type('Bolt3DResult', (), {
                'mesh': None,
                'format': 'unknown',
                'original_path': model_path,
                'type': 'bolt3d_result'
            })   
            return result
    
    def load_weights(self, weights_path: str):
        """Load model weights from a file.
        Args:
            weights_path (str): Path to the weights file  
        Returns:
            self: For method chaining  
        Note:
            This method is not used in the API version of the model,
            but is included for compatibility with the BaseModel interface.
        """
        logger.warning("load_weights() is not used in API mode")
        return self
    
    @property
    def name(self) -> str:
        """Get the name of the model.
        Returns:
            str: Model name
        """
        return "Bolt3D (API)"
