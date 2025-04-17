"""TRELLIS model integration for 3D generation using TRELLIS-3D API.
"""

import os
import logging
import tempfile
import time
from typing import Any, Dict, Optional, Union, List, Tuple
from pathlib import Path
import numpy as np
from PIL import Image

from threedify.models.base import BaseModel

try:
    from gradio_client import Client, handle_file
except ImportError:
    raise ImportError(
        "gradio_client is required for API access to TRELLIS. "
        "Install it with: pip install gradio_client"
    )
logger = logging.getLogger(__name__)

class TrellisModel(BaseModel):
    """TRELLIS model for generating 3D models from images using the TRELLIS-3D API.
    This model leverages the Hugging Face hosted TRELLIS API for high-quality 3D asset generation.
    """
    def __init__(self, api_url: str = "Steven18/trellis-3d-api"):
        """Initialize the TRELLIS model API client.
        Args:
            api_url (str): URL to the TRELLIS-3D API (default uses the official HF space)
        """
        self._api_url = api_url
        self._client = None
        self._session_active = False
    
    def generate(self, data: Any, **kwargs) -> Any:
        """Generate a 3D model from input data.
        Args:
            data: Input data (image or text prompt)git 
            **kwargs: Additional parameters
                - seed (int): Random seed for generation
                - ss_guidance_strength (float): Structure guidance strength (default: 7.5)
                - ss_sampling_steps (int): Structure sampling steps (default: 12)
                - slat_guidance_strength (float): Detail guidance strength (default: 3.0)
                - slat_sampling_steps (int): Detail sampling steps (default: 12)
                - mesh_simplify (float): Mesh simplification ratio (default: 0.95)
                - texture_size (int): Texture resolution (default: 1024)
                - multi_images (list): List of additional input images for multi-view
                - output_format (str): Output format (glb or gaussian, default: glb)          
        Returns:
            Generated 3D model data
        """
        if self._client is None:
            self._connect_api()
        if not self._session_active:
            self._start_session()
        image_path = self._preprocess(data)

        try:
            logger.info("Preprocessing image")
            result = self._client.predict(
                    image=handle_file(image_path),
                    is_multiimage="false",
                    seed=0,
                    ss_guidance_strength=7.5,
                    ss_sampling_steps=12,
                    slat_guidance_strength=3,
                    slat_sampling_steps=12,
                    multiimage_algo="stochastic",
                    mesh_simplify=0.95,
                    texture_size=1024,
                    api_name="/quick_generate_glb"
            )
            print(f"Result file path: {result}")
            model_path, download_path = result

            return model_path, download_path
            
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise
    
    def _connect_api(self):
        """Connect to the TRELLIS API.
        """
        logger.info(f"Connecting to TRELLIS API at {self._api_url}")
        try:
            self._client = Client(self._api_url)
            logger.info("Connected to TRELLIS API successfully")   
        except Exception as e:
            logger.error(f"Failed to connect to TRELLIS API: {str(e)}")
            raise
    
    def _start_session(self):
        """Start a session with the TRELLIS API.
        """
        logger.info("Starting TRELLIS API session") 
        try:
            self._client.predict(api_name="/start_session")
            self._session_active = True
            logger.info("TRELLIS API session started successfully")    
        except Exception as e:
            logger.error(f"Failed to start TRELLIS API session: {str(e)}")
            self._session_active = False
            raise
    
    def _preprocess(self, data):
        """Placeholder - Preprocess input data for TRELLIS.
        Args:
            data: Input data    
        Returns:
            Preprocessed data ready for TRELLIS API
        """
        return data
    
    def _postprocess(self, model_path, download_path, output_format):
        """Postprocess TRELLIS output.
        Args:
            model_path: Path to the generated model for display
            download_path: Path to the downloadable model file
            output_format: Format of the model 
        Returns:
            Processed results in a standard format
        """
        result_data = {} 
        if output_format == 'glb':
            try:
                import trimesh
                mesh = trimesh.load(download_path) 
                result_data['mesh'] = {
                    'vertices': np.array(mesh.vertices),
                    'faces': np.array(mesh.faces)
                }
                if hasattr(mesh.visual, 'material'):
                    if hasattr(mesh.visual.material, 'image'):
                        result_data['mesh']['texture'] = mesh.visual.material.image
                if hasattr(mesh.visual, 'uv'):
                    result_data['mesh']['uvs'] = mesh.visual.uv
                    
            except Exception as e:
                logger.warning(f"Could not load GLB with trimesh: {str(e)}")
                result_data['mesh'] = None
                
            result_data['format'] = 'glb'
                
        elif output_format == 'gaussian':
            # i cannot find any direct way to parse Gaussian models in Python
            # So I just store the path and let the user take care of it
            result_data['gaussian'] = True
            result_data['format'] = 'gaussian'
        result_data['display_path'] = model_path
        result_data['download_path'] = download_path
        result_data['type'] = 'trellis_result'
        result = type('TrellisResult', (), result_data)
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
        """
        Get the name of the model.
        
        Returns:
            str: Model name
        """
        return "TRELLIS (API)"
