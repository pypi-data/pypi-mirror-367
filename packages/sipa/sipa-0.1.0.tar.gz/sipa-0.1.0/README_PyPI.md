# SIPA - Simple Image Processing Application

A PyQt5-based GUI application for educational image processing operations. This package provides basic image processing functionality implemented from scratch using only NumPy (no advanced image processing libraries).

## Features

### Color Operations
- RGB to Grayscale conversion
- Binary thresholding (single and double)
- RGB channel transformations
- Contrast adjustment

### Geometric Operations
- 90-degree rotation
- Image cropping
- Zoom in/out functionality

### Filtering Operations
- Mean filter (blur)
- Median filter (noise reduction)
- Salt and pepper noise addition/removal
- Unsharp masking (sharpening)
- Prewitt edge detection

### Morphological Operations
- Erosion
- Dilation
- Opening
- Closing

### Histogram Operations
- Histogram calculation (grayscale and RGB)
- Histogram equalization
- Histogram stretching
- Histogram visualization

### Arithmetic Operations
- Weighted image addition
- Image division

## Installation

### From PyPI
```bash
pip install sipa
```

### From Source
```bash
git clone https://github.com/haydarkadioglu/simple-image-processing-application.git
cd simple-image-processing-application
pip install -e .
```

## Usage

### As a GUI Application
```bash
sipa
```

### As a Python Library
```python
import sipa
import numpy as np

# Load your image as a numpy array
image = np.array(...)  # Your image data

# Convert to grayscale
gray_image = sipa.Colors.convert_to_gray(image)

# Apply filters
filtered_image = sipa.Filters.mean_filter(gray_image, kernel_size=5)

# Detect edges
edges = sipa.Filters.detect_edge_prewitt(gray_image)

# Apply morphological operations
eroded = sipa.Histogram.erode(gray_image, kernel_size=3)
```

## Requirements

- Python >= 3.7
- NumPy >= 1.19.0
- PyQt5 >= 5.15.0
- matplotlib >= 3.3.0
- opencv-python >= 4.5.0

## Development

### Installing Development Dependencies
```bash
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black sipa/
```

### Linting
```bash
flake8 sipa/
```

## Educational Purpose

This project was created for educational purposes to help people understand basic image processing concepts. All image processing operations are implemented from scratch using only NumPy, making it easy to understand the underlying algorithms.

## Screenshots

![Main Interface](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/884d7e47-7c82-49f7-933e-3274f0199ad8)

![Double Threshold](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/e2206e25-d98f-43e0-8c33-7d69836442f5)

![Filtering Operations](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/a24e3787-2958-462c-98cf-fd961b54ffb5)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

**Haydar Kadıoğlu**
- GitHub: [@haydarkadioglu](https://github.com/haydarkadioglu)

## Acknowledgments

- This project is designed for educational purposes
- All image processing algorithms are implemented from scratch for learning
- Special thanks to the computer vision and image processing community
