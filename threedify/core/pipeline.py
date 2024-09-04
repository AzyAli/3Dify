"""Core pipeline implementation for 3dify.
This module provides the main processing pipeline for converting geospatial data to 3D models.
"""
import os
import logging
from typing import Dict, List, Union, Optional, Any
from pathlib import Path
import numpy as np

from threedify.core.config import Config
from threedify.data.loaders.import get_loader
from threedify.models import get_model
from threedify.processing import get_processor
from threedify.export import get_exporter
from threedify.visualization import get_visualizer

logger = logging.getLogger(__name__)

class Pipeline:
    """Main processing pipeline for converting geospatial data to 3D models.
    This class manages the entire workflow, including loading data, processing it,
    and exporting the final 3D model.
    """
    def __init__(self, config: Optional[Dict] = None, verbose: bool = True):
        """Initialize the pipeline with a configuration dictionary.
        Args:
            config (dict, optional): Configuration parameters for the pipeline
            verbose (bool): Whether to display verbose output
        """
        self.config = Config(config)
        self.verbose = verbose
        self._setup_logging()
        #to be inistialized when needed/it is what it is just tired staring at the screen
        self._loader = None
        self._model = None
        self._processor = None
        self._exporter = None
        self._visualizer = None
        self.results = {} # Store results heeere
        if self.verbose:
            logger.info("Pipeline initialized with configuration: %s", self.config)
    
    def _setup_logging(self):
        """Set up logging configuration."""
        level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    
    def load(self, data_path: Union[str, Path], data_type: Optional[str] = None, **kwargs):
        """Load input data.
        Args:
            data_path (str or Path): Path to the input data file
            data_type (str, optional): Type of data to load If not specified, will be inferred or just specify it dont be lazy!
            **kwargs: Additional keyword arguments for the loader
        Returns:
            self: Pipeline instance for method chaining
        """
        if data_type is None:
            data_type = self._infer_data_type(data_path)
            logger.info("Inferred data type: %s", data_type)
        self._loader = get_loader(data_type)
        if self.verbose:
            logger.info("Loading data from %s of type %s", data_path, data_type)
        self.data = self._loader.load(data_path, **kwargs)
        if self.verbose:
            logger.info("%s Data loaded successfully", data_type)
        return self
    
    def process(self, processor_type: Optional[str] = None, **kwargs):
        """Process the loaded data.
        Args:
            processor_type (str, optional): Type of processor to use If not specified, will be inferred
            **kwargs: Additional keyword arguments for the processor
        Returns:
            self: Pipeline instance for method chaining
        """
        if not hasattr(self, 'data'):
            raise ValueError("No data loaded. Please call load() first.")
        if processor_type is None:
            processor_type = self._infer_processor_type()
        self._processor = get_processor(processor_type)
        if self.verbose:
            logger.info("Processing data with %s processor", processor_type)
        self.processed_data = self._processor.process(self.data, **kwargs)
        self.results['processed_data'] = self.processed_data
        if self.verbose:
            logger.info("Data processed successfully")
        return self

    def generate_model(self, model_type: str = "bolt3d", **kwargs):
        """Generate a 3D model from the processed data.
        Args:
            model_type (str): Type of model to use (bolt3d or trellis)
            **kwargs: Additional keyword arguments for the model
        Returns:
            self: Pipeline instance for method chaining
        """
        if not hasattr(self, 'processed_data'):
            raise ValueError("No processed data available. Please call process() first.")
        self._model = get_model(model_type)
        if self.verbose:
            logger.info("Generating 3d model using %s", model_type)
        self.model_data = self._model.generate(self.processed_data, **kwargs)
        self.results['model_data'] = self.model_data
        if self.verbose:
            logger.info("3D model generated successfully")
        return self
    
    def export(self, output_path: Union[str, Path], format_type: str = "gltf", **kwargs):
        """Export the generated 3D model to the specified format.
        Args:
            output_path (str or Path): Path to save the exported model
            format_type (str): Format to export the model (e.g., gltf, obj)
            **kwargs: Additional keyword arguments for the exporter
        Returns:
            self: Pipeline instance for method chaining
        """
        if not hasattr(self, 'model_data'):
            raise ValueError("No model data available. Please call generate_model() first.")
        output_path = Path(output_path)
        os.makedirs(output_path.parent, exist_ok=True)
        self._exporter = get_exporter(format_type)
        if self.verbose:
            logger.info("Exporting model to %s format at %s", format_type, output_path)
        exporter_path = self._exporter.export(self.model_data, output_path, **kwargs)
        self.results['exporter_path'] = exporter_path
        if self.verbose:
            logger.info("Model exported successfully to %s", exporter_path)
        return self
    
    def visualize(self, visualization_type: str = "jupyter", **kwargs):
        """Visualize the generated 3D model.
        Args:
            visualizer_type (str): Type of visualizer to use (e.g., jupyter, plotly)
            **kwargs: Additional keyword arguments for the visualizer
        Returns:
            self: Pipeline instance for method chaining
        """
        if not hasattr(self, 'model_data'):
            raise ValueError("No model data available. Please call generate_model() first.")
        self._visualizer = get_visualizer(visualization_type)
        if self.verbose:
            logger.info("Visualizing model using %s", visualization_type)
        visualization = self._visualizer.visualize(self.model_data, **kwargs)
        return visualization
    
    def _infer_data_type(self, data_path: Union[str, Path]) -> str:
        """Infer the data type based on the file extension.
        Args:
            data_path (Path): Path to the data file
        Returns:
            str: Inferred data type
        """
        extension = data_path.suffix.lower()
        if extension in ['.las', '.laz']:
            return 'lidar'
        elif extension in ['.tif', '.tiff', '.jpg', '.jpeg', '.png']:
            return 'raster'
        elif extension in ['.shp', '.geojson']:
            return 'vector'
        elif extension in ['.csv', '.txt']:
            return 'tabular'
        else:
            raise ValueError(f"Unsupported data type for file: {data_path}. Supported types are: lidar, raster, vector, tabular.")
    
    def _infer_processor_type(self) -> str:
        """Infer the processor type based on the loaded data.
        Returns:
            str: Inferred processor type
        """
        if hasattr(self, 'data'):
            if hasattr(self.data, 'point_cloud'):
                return 'point_cloud'
            elif hasattr(self.data, 'raster'):
                return 'raster'
            elif hasattr(self.data, 'vector'):
                return 'vector'
        
        return 'general'
    
    def run_pipeline(self, data_path: Union[str, Path], output_path: Union[str, Path], data_type: Optional[str] = None, processor_type: Optional[str] = None, model_type: str = "bolt3d", format_type: str = "gltf", **kwargs):
        """Run the entire pipeline from loading data to exporting the model.
        Args:
            data_path (str or Path): Path to the input data file
            output_path (str or Path): Path to save the exported model
            data_type (str, optional): Type of data to load If not specified, will be inferred
            processor_type (str, optional): Type of processor to use If not specified, will be inferred
            model_type (str): Type of model to use (bolt3d or trellis)
            format_type (str): Format to export the model (e.g., gltf, obj)
            **kwargs: Additional keyword arguments for each step
        Returns:
            self: Pipeline instance for method chaining
        """
        return (self
            .load(data_path, data_type, **kwargs.get('load_kwargs', {}))
            .process(processor_type, **kwargs.get('process_kwargs', {}))
            .generate_model(model_type, **kwargs.get('model_kwargs', {}))
            .export(output_path, format_type, **kwargs.get('export_kwargs', {}))
        )