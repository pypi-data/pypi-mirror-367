# Example usage of SIPA library

import numpy as np
from sipa.core import Colors, Filters, Histogram

# Example 1: Create a simple test image
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

# Example 2: Color operations
def example_color_operations():
    """Demonstrate color operations."""
    print("=== Color Operations Example ===")
    
    # Create test image
    rgb_image = create_test_image()
    print(f"Original image shape: {rgb_image.shape}")
    
    # Convert to grayscale
    gray_image = Colors.convert_to_gray(rgb_image)
    print(f"Grayscale image shape: {gray_image.shape}")
    
    # Convert to binary
    binary_image = Colors.convert_to_binary(gray_image, 128)
    print(f"Binary image unique values: {np.unique(binary_image)}")
    
    # Apply single threshold
    thresh_image = Colors.single_threshold(gray_image, 100)
    print(f"Threshold image unique values: {np.unique(thresh_image)}")
    
    return gray_image

# Example 3: Filter operations
def example_filter_operations(image):
    """Demonstrate filter operations."""
    print("\n=== Filter Operations Example ===")
    
    # Apply mean filter
    mean_filtered = Filters.mean_filter(image, 5)
    print(f"Mean filtered image shape: {mean_filtered.shape}")
    
    # Apply median filter
    median_filtered = Filters.median_filter(image, 5)
    print(f"Median filtered image shape: {median_filtered.shape}")
    
    # Add salt and pepper noise
    noisy_image = Filters.salt_pepper(image, 100)
    print(f"Added 100 noise pixels")
    
    # Detect edges
    edges = Filters.detect_edge_prewitt(image)
    print(f"Edge detection completed, shape: {edges.shape}")

# Example 4: Histogram operations
def example_histogram_operations(image):
    """Demonstrate histogram operations."""
    print("\n=== Histogram Operations Example ===")
    
    # Calculate histogram
    hist = Histogram.calculate_gray_histogram(image)
    print(f"Histogram calculated, non-zero bins: {np.count_nonzero(hist)}")
    
    # Apply histogram equalization
    equalized = Histogram.histogram_equalization(np.stack([image] * 3, axis=-1))
    print(f"Histogram equalized image shape: {equalized.shape}")
    
    # Apply histogram stretching
    stretched = Histogram.histogram_stretching(image)
    print(f"Histogram stretched image range: {np.min(stretched)} - {np.max(stretched)}")

# Example 5: Morphological operations
def example_morphological_operations(image):
    """Demonstrate morphological operations."""
    print("\n=== Morphological Operations Example ===")
    
    # Convert to binary for morphological operations
    binary = Colors.convert_to_binary(image, 128)
    
    # Apply erosion
    eroded = Histogram.erode(binary, 3)
    print(f"Erosion applied, unique values: {np.unique(eroded)}")
    
    # Apply dilation
    dilated = Histogram.dilate(binary, 3)
    print(f"Dilation applied, unique values: {np.unique(dilated)}")
    
    # Apply opening
    opened = Histogram.opening(binary, 3)
    print(f"Opening applied, unique values: {np.unique(opened)}")
    
    # Apply closing
    closed = Histogram.closing(binary, 3)
    print(f"Closing applied, unique values: {np.unique(closed)}")

if __name__ == "__main__":
    print("SIPA Library Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        gray_image = example_color_operations()
        example_filter_operations(gray_image)
        example_histogram_operations(gray_image)
        example_morphological_operations(gray_image)
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("You can now use 'sipa' command to launch the GUI application.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
