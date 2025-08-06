"""
Test module for SIPA core functionality.
"""

import pytest
import numpy as np
from sipa.core import Colors, Filters, Histogram, Rotate, Aritmatich


class TestColors:
    """Test color operations."""
    
    def test_convert_to_gray(self):
        """Test RGB to grayscale conversion."""
        # Create a test RGB image
        rgb_image = np.ones((10, 10, 3), dtype=np.uint8) * 128
        gray_image = Colors.convert_to_gray(rgb_image)
        
        assert gray_image.shape == (10, 10)
        assert gray_image.dtype == np.uint8
        
    def test_convert_to_binary(self):
        """Test binary conversion."""
        gray_image = np.random.randint(0, 255, (10, 10), dtype=np.uint8)
        binary_image = Colors.convert_to_binary(gray_image, 128)
        
        assert binary_image.shape == gray_image.shape
        assert np.all((binary_image == 0) | (binary_image == 255))


class TestFilters:
    """Test filter operations."""
    
    def test_mean_filter(self):
        """Test mean filter."""
        image = np.ones((10, 10), dtype=np.uint8) * 100
        filtered = Filters.mean_filter(image, 3)
        
        assert filtered.shape == image.shape
        assert filtered.dtype == image.dtype
        
    def test_median_filter(self):
        """Test median filter."""
        image = np.ones((10, 10), dtype=np.uint8) * 100
        filtered = Filters.median_filter(image, 3)
        
        assert filtered.shape == image.shape
        assert filtered.dtype == image.dtype


class TestHistogram:
    """Test histogram operations."""
    
    def test_calculate_gray_histogram(self):
        """Test grayscale histogram calculation."""
        image = np.ones((10, 10), dtype=np.uint8) * 128
        hist = Histogram.calculate_gray_histogram(image)
        
        assert len(hist) == 256
        assert hist[128] == 100  # All pixels have value 128
        
    def test_erode(self):
        """Test morphological erosion."""
        image = np.ones((10, 10), dtype=np.uint8) * 255
        eroded = Histogram.erode(image, 3)
        
        assert eroded.shape == image.shape
        assert eroded.dtype == image.dtype


class TestRotate:
    """Test geometric operations."""
    
    def test_crop(self):
        """Test image cropping."""
        image = np.ones((20, 20, 3), dtype=np.uint8)
        cropped = Rotate.crop(image, 5, 5, 15, 15)
        
        assert cropped.shape == (10, 10, 3)
        
    def test_zoom(self):
        """Test image zooming."""
        image = np.ones((10, 10), dtype=np.uint8)
        zoomed = Rotate.zoom(image, 2.0)
        
        assert zoomed.shape == (20, 20)


class TestAritmatich:
    """Test arithmetic operations."""
    
    def test_add_weighted(self):
        """Test weighted addition."""
        img1 = np.ones((10, 10, 3), dtype=np.uint8) * 100
        img2 = np.ones((10, 10, 3), dtype=np.uint8) * 50
        result = Aritmatich.add_weighted(img1, 0.5, img2, 0.5)
        
        assert result.shape == img1.shape
        assert result.dtype == np.uint8


if __name__ == "__main__":
    pytest.main([__file__])
