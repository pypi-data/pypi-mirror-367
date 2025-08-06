# LEGACY Import Example - Backward Compatibility

"""
This example shows how to use SIPA with the legacy import structure.
This is for backward compatibility with existing code.
"""

# Legacy import style
from Functions import SIP as sip
import numpy as np
import matplotlib.pyplot as plt

def create_test_image():
    """Create a simple test image with gradients."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Create gradient patterns
    for i in range(100):
        for j in range(100):
            image[i, j, 0] = int(255 * i / 100)  # Red gradient
            image[i, j, 1] = int(255 * j / 100)  # Green gradient
            image[i, j, 2] = 128  # Constant blue
            
    return image

def legacy_usage_example():
    """Demonstrate legacy usage with old import structure."""
    print("=== Legacy Import Style Example ===")
    
    # Create test image
    rgb_image = create_test_image()
    print(f"Original image shape: {rgb_image.shape}")
    
    # Color operations using legacy syntax
    gray_image = sip.Colors.convert_to_gray(rgb_image)
    print(f"Grayscale conversion: {gray_image.shape}")
    
    binary_image = sip.Colors.convert_to_binary(gray_image, 128)
    print(f"Binary conversion: unique values = {np.unique(binary_image)}")
    
    # Filter operations using legacy syntax
    mean_filtered = sip.Filters.mean_filter(gray_image, 5)
    print(f"Mean filter applied: {mean_filtered.shape}")
    
    median_filtered = sip.Filters.median_filter(gray_image, 5)
    print(f"Median filter applied: {median_filtered.shape}")
    
    # Edge detection using legacy syntax
    edges = sip.Filters.detect_edge_prewitt(gray_image)
    print(f"Edge detection: {edges.shape}")
    
    # Geometric operations using legacy syntax
    rotated = sip.Rotate.rotate_image(rgb_image)
    print(f"Rotation: {rotated.shape}")
    
    cropped = sip.Rotate.crop(rgb_image, 20, 20, 80, 80)
    print(f"Cropping: {cropped.shape}")
    
    zoomed = sip.Rotate.zoom(gray_image, 0.5)
    print(f"Zoom: {zoomed.shape}")
    
    # Histogram operations using legacy syntax
    hist = sip.Histogram.calculate_gray_histogram(gray_image)
    print(f"Histogram calculated: {len(hist)} bins")
    
    # Morphological operations using legacy syntax
    eroded = sip.Histogram.erode(binary_image, 3)
    print(f"Erosion: unique values = {np.unique(eroded)}")
    
    dilated = sip.Histogram.dilate(binary_image, 3)
    print(f"Dilation: unique values = {np.unique(dilated)}")
    
    print("\n✅ All legacy operations completed successfully!")
    print("This code maintains backward compatibility with existing projects.")

if __name__ == "__main__":
    try:
        legacy_usage_example()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have the Functions module available or install sipa package.")
