"""Basic test for threedify pipeline with image input.
"""

import unittest
import os
import tempfile
from pathlib import Path
from PIL import Image
import numpy as np

from threedify.core.pipeline import Pipeline

class TestPipeline():
    """Test cases for the threedify pipeline."""
    def setUp(self):
        """Set up test environment."""
        self.test_dir = "test_sample"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.test_image_path = os.path.join(self.test_dir, "bus.png")
        # self._create_test_image(self.test_image_path)
        self.pipeline = Pipeline()
    
    def _create_test_image(self, path):
        """Create a simple test image."""
        size = 256
        img = Image.new('RGB', (size, size), color='white')
        pixels = img.load()
        
        for i in range(size):
            for j in range(size):
                if (i // 32 + j // 32) % 2 == 0:
                    pixels[i, j] = (0, 0, 0)
        img.save(path)
    
    def test_load_image(self):
        """Test loading an image into the pipeline."""
        _ = self.pipeline.load(self.test_image_path, data_type="raster")
    
    def test_process_image(self):
        """Test processing an image."""
        _ = self.pipeline.load(self.test_image_path, data_type="raster")
        _ = self.pipeline.process(process_type="raster")

    def test_full_pipeline(self):
        """Test running the full pipeline."""
        output_path = self.test_dir
        result = self.pipeline.run_pipeline(
            data_path=self.test_image_path,
            output_path=output_path,
            data_type="raster",
            process_type="raster",
            model_type="trellis",
            export_format="gltf"
        )
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_image_path):
            os.unlink(self.test_image_path)
        for file in os.listdir(self.test_dir):
            try:
                os.unlink(os.path.join(self.test_dir, file))
            except:
                pass
        try:
            os.rmdir(self.test_dir)
        except:
            pass

if __name__ == '__main__':
    test = TestPipeline()
    test.setUp()
    test.test_load_image()
    test.test_process_image()
    test.test_full_pipeline()