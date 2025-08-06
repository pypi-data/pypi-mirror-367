# MODERN Import Example - Recommended Usage

"""
This example shows how to use SIPA with the modern import structure.
This is the recommended way for new projects.
"""

import sipa
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

def modern_usage_example():
    """Demonstrate modern usage with new import structure."""
    print("=== Modern Import Style Example ===")
    print(f"SIPA Version: {sipa.__version__}")
    
    # Create test image
    rgb_image = create_test_image()
    print(f"Original image shape: {rgb_image.shape}")
    
    # Color operations using modern syntax
    gray_image = sipa.Colors.convert_to_gray(rgb_image)
    print(f"Grayscale conversion: {gray_image.shape}")
    
    binary_image = sipa.Colors.convert_to_binary(gray_image, 128)
    print(f"Binary conversion: unique values = {np.unique(binary_image)}")
    
    contrast_enhanced = sipa.Colors.increase_contrast(rgb_image, 1.5)
    print(f"Contrast enhanced: {contrast_enhanced.shape}")
    
    # Filter operations using modern syntax
    mean_filtered = sipa.Filters.mean_filter(gray_image, 5)
    print(f"Mean filter applied: {mean_filtered.shape}")
    
    median_filtered = sipa.Filters.median_filter(gray_image, 5)
    print(f"Median filter applied: {median_filtered.shape}")
    
    # Add some noise and then remove it
    noisy = sipa.Filters.salt_pepper(gray_image, 50)
    denoised = sipa.Filters.median_filter(noisy, 3)
    print(f"Noise added and removed: {denoised.shape}")
    
    # Edge detection using modern syntax
    edges = sipa.Filters.detect_edge_prewitt(gray_image)
    print(f"Edge detection: {edges.shape}")
    
    # Geometric operations using modern syntax
    rotated = sipa.Rotate.rotate_image(rgb_image)
    print(f"Rotation: {rotated.shape}")
    
    cropped = sipa.Rotate.crop(rgb_image, 20, 20, 80, 80)
    print(f"Cropping: {cropped.shape}")
    
    zoomed = sipa.Rotate.zoom(gray_image, 2.0)
    print(f"Zoom: {zoomed.shape}")
    
    # Histogram operations using modern syntax
    hist = sipa.Histogram.calculate_gray_histogram(gray_image)
    print(f"Histogram calculated: {len(hist)} bins, max count: {np.max(hist)}")
    
    rgb_hists = sipa.Histogram.calculate_rgb_histogram(rgb_image)
    print(f"RGB histograms calculated: R, G, B channels")
    
    stretched = sipa.Histogram.histogram_stretching(gray_image)
    print(f"Histogram stretched: range [{np.min(stretched)}, {np.max(stretched)}]")
    
    # Morphological operations using modern syntax
    eroded = sipa.Histogram.erode(binary_image, 3)
    print(f"Erosion: unique values = {np.unique(eroded)}")
    
    dilated = sipa.Histogram.dilate(binary_image, 3)
    print(f"Dilation: unique values = {np.unique(dilated)}")
    
    opened = sipa.Histogram.opening(binary_image, 3)
    print(f"Opening: unique values = {np.unique(opened)}")
    
    closed = sipa.Histogram.closing(binary_image, 3)
    print(f"Closing: unique values = {np.unique(closed)}")
    
    print("\n✅ All modern operations completed successfully!")
    print("This is the recommended way to use SIPA in new projects.")

def visualization_example():
    """Show how to visualize results."""
    print("\n=== Visualization Example ===")
    
    # Create test image
    image = create_test_image()
    
    # Apply various operations
    gray = sipa.Colors.convert_to_gray(image)
    binary = sipa.Colors.convert_to_binary(gray, 128)
    edges = sipa.Filters.detect_edge_prewitt(gray)
    blurred = sipa.Filters.mean_filter(gray, 5)
    
    # Create visualization
    plt.figure(figsize=(15, 3))
    
    plt.subplot(1, 5, 1)
    plt.imshow(image)
    plt.title('Original')
    plt.axis('off')
    
    plt.subplot(1, 5, 2)
    plt.imshow(gray, cmap='gray')
    plt.title('Grayscale')
    plt.axis('off')
    
    plt.subplot(1, 5, 3)
    plt.imshow(binary, cmap='gray')
    plt.title('Binary')
    plt.axis('off')
    
    plt.subplot(1, 5, 4)
    plt.imshow(edges, cmap='gray')
    plt.title('Edges')
    plt.axis('off')
    
    plt.subplot(1, 5, 5)
    plt.imshow(blurred, cmap='gray')
    plt.title('Blurred')
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig('sipa_examples.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("Visualization saved as 'sipa_examples.png'")

if __name__ == "__main__":
    try:
        modern_usage_example()
        visualization_example()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure you have installed sipa: pip install sipa")
