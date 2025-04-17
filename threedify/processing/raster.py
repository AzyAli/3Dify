"""Raster processing module for geospatial imagery analysis.
"""

import logging
from typing import Any, Dict, Optional, List, Tuple, Union
import numpy as np

from threedify.processing.base import BaseProcessor

logger = logging.getLogger(__name__)
class RasterProcessor(BaseProcessor):
    """Processor for raster data (satellite imagery, aerial photos, etc.)."""
    def process(self, data: Any, **kwargs) -> Any:
        """Process raster imagery.
        Args:
            data: Input raster data
            **kwargs: Additional processor-specific parameters
                - resize (tuple): Target size (width, height)
                - enhance (bool): Whether to enhance the image
                - extract_features (bool): Whether to extract features
                - building_mode (bool): Special processing for buildings
                - denoise (bool): Apply denoising algorithms
                - normalize (bool): Apply normalization to pixel values
                - contrast_stretch (tuple): Apply contrast stretching (min_percentile, max_percentile)    
        Returns:
            Processed raster data
        """
        logger.info("Processing raster data")
        
        if hasattr(data, 'image'):
            image = data.image
            image_array = data.array
            metadata = getattr(data, 'metadata', {})
        else:
            from PIL import Image
            if isinstance(data, Image.Image):
                image = data
                image_array = np.array(image)
                metadata = {
                    'width': image.width,
                    'height': image.height,
                    'mode': image.mode
                }
            else:
                image_array = data
                image = Image.fromarray(image_array if image_array.dtype == np.uint8 
                                       else (image_array * 255).astype(np.uint8))
                metadata = {}
        resize = kwargs.get('resize', None)
        enhance = kwargs.get('enhance', False)
        extract_features = kwargs.get('extract_features', True)
        building_mode = kwargs.get('building_mode', False)
        denoise = kwargs.get('denoise', False)
        normalize = kwargs.get('normalize', False)
        contrast_stretch = kwargs.get('contrast_stretch', None)
        processed_image = image.copy()
        processed_array = image_array.copy()
        if normalize:
            processed_array, processed_image = self._normalize(processed_array)
        if contrast_stretch:
            processed_array, processed_image = self._contrast_stretch(processed_array, *contrast_stretch)
        if denoise:
            processed_array, processed_image = self._denoise(processed_array)
        if resize:
            processed_image, processed_array = self._resize(processed_image, resize)
        if enhance:
            processed_image, processed_array = self._enhance(processed_image)
        if extract_features:
            features = self._extract_features(processed_array)
        else:
            features = None
        if building_mode:
            processed_image, processed_array, building_segments = self._process_building(
                processed_image, processed_array)
        else:
            building_segments = None
        processed_data = type('ProcessedRaster', (), {
            'image': processed_image,
            'array': processed_array,
            'features': features,
            'building_segments': building_segments,
            'metadata': metadata,
            'original_data': data,
            'type': 'processed_raster'
        })
        logger.info("Raster processing complete")
        return processed_data
    
    def _resize(self, image, target_size: Tuple[int, int]):
        """Resize an image.
        Args:
            image: PIL Image to resize
            target_size (tuple): Target size (width, height)  
        Returns:
            tuple: Resized image and array
        """
        logger.info(f"Resizing image to {target_size}")
        resized_image = image.resize(target_size, resample=image.LANCZOS)
        resized_array = np.array(resized_image)
        return resized_image, resized_array
    
    def _normalize(self, image_array):
        """Normalize image pixel values to range [0, 1].
        Args:
            image_array: Numpy array of image  
        Returns:
            tuple: Normalized array and corresponding PIL Image
        """
        logger.info("Normalizing image values")
        if image_array.dtype == np.uint8:
            normalized = image_array.astype(np.float32) / 255.0
        else:
            min_val = np.min(image_array)
            max_val = np.max(image_array)
            normalized = (image_array - min_val) / (max_val - min_val + 1e-10)
        normalized_uint8 = (normalized * 255).astype(np.uint8)
        from PIL import Image
        normalized_image = Image.fromarray(normalized_uint8)
        return normalized, normalized_image
    
    def _contrast_stretch(self, image_array, min_percentile=2, max_percentile=98):
        """Apply contrast stretching to enhance image details.
        Args:
            image_array: Numpy array of image
            min_percentile: Lower percentile for clipping
            max_percentile: Upper percentile for clipping
        Returns:
            tuple: Contrast-stretched array and PIL Image
        """
        logger.info(f"Applying contrast stretching ({min_percentile}%, {max_percentile}%)")
        p_low = np.percentile(image_array, min_percentile)
        p_high = np.percentile(image_array, max_percentile)
        stretched = np.clip(image_array, p_low, p_high)
        stretched = (stretched - p_low) / (p_high - p_low + 1e-10)
        stretched_uint8 = (stretched * 255).astype(np.uint8)
        from PIL import Image
        stretched_image = Image.fromarray(stretched_uint8)
        return stretched, stretched_image
    
    def _denoise(self, image_array):
        """Apply denoising to the image.
        Args:
            image_array: Numpy array of image 
        Returns:
            tuple: Denoised array and PIL Image
        """
        logger.info("Applying denoising algorithm")
        import cv2
        if len(image_array.shape) == 3:  # Color image
            denoised = cv2.fastNlMeansDenoisingColored(
                image_array.astype(np.uint8), None, 10, 10, 7, 21)
        else:  
            denoised = cv2.fastNlMeansDenoising(
                image_array.astype(np.uint8), None, 10, 7, 21)
        from PIL import Image
        denoised_image = Image.fromarray(denoised)
        return denoised, denoised_image
    
    def _enhance(self, image):
        """Enhance an image with multiple techniques.
        Args:
            image: PIL Image to enhance  
        Returns:
            tuple: Enhanced image and array
        """
        logger.info("Enhancing image with multiple techniques")
        from PIL import ImageEnhance, ImageFilter
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Brightness(enhanced)
        enhanced = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Color(enhanced)
        enhanced = enhancer.enhance(1.1)
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=2.0, percent=150))
        enhanced_array = np.array(enhanced)
        return enhanced, enhanced_array
    
    def _extract_features(self, image_array: np.ndarray) -> Dict:
        """Extract features from an image using computer vision techniques.
        Args:
            image_array (np.ndarray): Image as numpy array 
        Returns:
            dict: Extracted features
        """
        logger.info("Extracting features from image")
        import cv2
        features = {
            'mean': np.mean(image_array, axis=(0, 1)),
            'std': np.std(image_array, axis=(0, 1)),
            'min': np.min(image_array, axis=(0, 1)),
            'max': np.max(image_array, axis=(0, 1)),
        }
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array.astype(np.uint8)
        edges = cv2.Canny(gray, 100, 200)
        features['edge_density'] = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        try:
            sift = cv2.SIFT_create()
            keypoints = sift.detect(gray, None)
            features['keypoint_count'] = len(keypoints)
            if keypoints:
                strengths = [kp.response for kp in keypoints]
                features['keypoint_mean_strength'] = np.mean(strengths)
                features['keypoint_max_strength'] = np.max(strengths)
        except:
            features['keypoint_count'] = 0
            features['keypoint_mean_strength'] = 0
            features['keypoint_max_strength'] = 0 
        try:
            from skimage.feature import graycomatrix, graycoprops
            if gray.shape[0] > 1000 or gray.shape[1] > 1000:
                factor = max(1, min(gray.shape[0], gray.shape[1]) // 1000)
                gray_small = gray[::factor, ::factor]
            else:
                gray_small = gray
            gray_small = (gray_small / 16).astype(np.uint8)
            glcm = graycomatrix(gray_small, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 
                               levels=16, symmetric=True, normed=True)
            features['contrast'] = graycoprops(glcm, 'contrast').mean()
            features['dissimilarity'] = graycoprops(glcm, 'dissimilarity').mean()
            features['homogeneity'] = graycoprops(glcm, 'homogeneity').mean()
            features['energy'] = graycoprops(glcm, 'energy').mean()
            features['correlation'] = graycoprops(glcm, 'correlation').mean()
        except Exception as e:
            logger.warning(f"Could not compute texture features: {str(e)}")    
        return features
    
    def _process_building(self, image, image_array: np.ndarray) -> Tuple:
        """Apply specialized processing for buildings using more advanced techniques.
        Args:
            image: PIL Image to process
            image_array (np.ndarray): Image as numpy array  
        Returns:
            tuple: Processed image, array, and building segments
        """
        logger.info("Applying specialized processing for buildings")
        import cv2
        import numpy as np
        image_array_uint8 = image_array.astype(np.uint8)
        if len(image_array_uint8.shape) == 3 and image_array_uint8.shape[2] == 3:
            grayscale = cv2.cvtColor(image_array_uint8, cv2.COLOR_RGB2GRAY)
        else:
            grayscale = image_array_uint8
        blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        contours, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_building_area = grayscale.shape[0] * grayscale.shape[1] * 0.01  # 1% of image area
        building_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_building_area]
        result_array = image_array_uint8.copy()
        cv2.drawContours(result_array, building_contours, -1, (0, 0, 255), 2)
        building_masks = []
        for i, cnt in enumerate(building_contours):
            mask = np.zeros_like(grayscale)
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            building_masks.append(mask)
        edges = cv2.Canny(grayscale, 100, 200)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(result_array, (x1, y1), (x2, y2), (0, 255, 0), 1)
        from PIL import Image
        result_image = Image.fromarray(result_array)
        building_segments = {
            'edges': edges,
            'contours': building_contours,
            'masks': building_masks,
            'count': len(building_contours),
            'lines': lines if lines is not None else [],
            'areas': [cv2.contourArea(cnt) for cnt in building_contours],
            'bounding_boxes': [cv2.boundingRect(cnt) for cnt in building_contours]
        }
        building_segments['centroids'] = []
        for cnt in building_contours:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                building_segments['centroids'].append((cX, cY))
            else:
                building_segments['centroids'].append(None)
        return result_image, result_array, building_segments
    
    @property
    def name(self) -> str:
        """
        Get the name of the processor.
        
        Returns:
            str: Processor name
        """
        return "raster"