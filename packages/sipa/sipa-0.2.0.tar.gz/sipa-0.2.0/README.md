# SIPA - Simple Image Processing Application

**A comprehensive educational tool for learning image processing fundamentals**

## 🎯 Project Goal

This application is designed to provide a simple and intuitive platform for learning image processing concepts. All image processing functions are implemented from scratch using only NumPy, making it perfect for educational purposes and understanding the underlying algorithms.

## ✨ Key Features

### 🎨 Color Operations
- **RGB to Grayscale Conversion**: Convert color images to grayscale using luminance formula
- **Binary Thresholding**: Single and double threshold operations
- **RGB Channel Manipulation**: Individual channel transformations
- **Contrast Enhancement**: Adjustable contrast control

### 🔧 Filtering Operations
- **Noise Reduction**: Mean and median filters
- **Edge Detection**: Prewitt operator implementation
- **Image Sharpening**: Unsharp masking technique
- **Noise Addition**: Salt and pepper noise for testing

### 📊 Histogram Operations
- **Histogram Analysis**: Calculate and display RGB/Grayscale histograms
- **Histogram Equalization**: Improve image contrast automatically
- **Histogram Stretching**: Enhance dynamic range

### 🔄 Geometric Transformations
- **Image Rotation**: 90-degree clockwise rotation
- **Cropping**: Select and extract image regions
- **Zooming**: Scale images up or down

### 🧮 Morphological Operations
- **Erosion & Dilation**: Basic morphological transformations
- **Opening & Closing**: Combined operations for noise removal
- **Binary Image Processing**: Optimized for binary images

### ➕ Arithmetic Operations
- **Image Addition**: Weighted combination of two images
- **Image Division**: Pixel-wise division operations

## 🚀 Installation & Usage

SIPA can be used in **two different ways**:

### 1. 📱 As a GUI Application (Recommended)

#### From PyPI
```bash
pip install sipa
sipa  # Launch GUI application
```

#### From Source
```bash
git clone https://github.com/haydarkadioglu/simple-image-processing-application.git
cd simple-image-processing-application
pip install -e .
sipa  # Launch GUI application
```

#### Direct Execution
```bash
# Clone the repository
git clone https://github.com/haydarkadioglu/simple-image-processing-application.git
cd simple-image-processing-application

# Install dependencies
pip install numpy matplotlib PyQt5 opencv-python

# Run directly
python main.py
```

### 2. 📚 As a Python Library

#### Modern Import Style (Recommended)
```python
import sipa
import numpy as np

# Load your image as numpy array
image = np.array(...)  # Your image data (height, width, 3) for RGB

# Convert to grayscale
gray_image = sipa.Colors.convert_to_gray(image)

# Apply filters
filtered = sipa.Filters.mean_filter(gray_image, kernel_size=5)
median_filtered = sipa.Filters.median_filter(image, kernel_size=3)

# Detect edges
edges = sipa.Filters.detect_edge_prewitt(gray_image)

# Geometric transformations
rotated = sipa.Rotate.rotate_image(image)
cropped = sipa.Rotate.crop(image, x1=10, y1=10, x2=100, y2=100)
zoomed = sipa.Rotate.zoom(image, factor=2.0)

# Morphological operations (for binary images)
binary = sipa.Colors.convert_to_binary(gray_image, threshold=128)
eroded = sipa.Histogram.erode(binary, kernel_size=3)
dilated = sipa.Histogram.dilate(binary, kernel_size=3)

# Histogram operations
hist = sipa.Histogram.calculate_gray_histogram(gray_image)
equalized = sipa.Histogram.histogram_equalization(image)
```

#### Legacy Import Style (Backward Compatibility)
```python
# For existing code that uses the old import structure
from Functions import SIP as sip
import numpy as np

image = np.array(...)  # Your image data

# Same functionality, old syntax
gray_image = sip.Colors.convert_to_gray(image)
filtered = sip.Filters.mean_filter(gray_image, 5)
edges = sip.Filters.detect_edge_prewitt(gray_image)
```

### 🎯 Quick Start Example
```python
import sipa
import numpy as np
import matplotlib.pyplot as plt

# Create a test image
test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

# Basic operations
gray = sipa.Colors.convert_to_gray(test_image)
binary = sipa.Colors.convert_to_binary(gray, 128)
blurred = sipa.Filters.mean_filter(gray, 5)
edges = sipa.Filters.detect_edge_prewitt(gray)

# Display results
plt.figure(figsize=(12, 3))
plt.subplot(1, 4, 1); plt.imshow(gray, cmap='gray'); plt.title('Grayscale')
plt.subplot(1, 4, 2); plt.imshow(binary, cmap='gray'); plt.title('Binary')
plt.subplot(1, 4, 3); plt.imshow(blurred, cmap='gray'); plt.title('Blurred')
plt.subplot(1, 4, 4); plt.imshow(edges, cmap='gray'); plt.title('Edges')
plt.show()
```

## 📸 Application Screenshots

**Main Interface - Image Selection**
![Screenshot 2024-05-27 004906](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/884d7e47-7c82-49f7-933e-3274f0199ad8)

**Double Threshold Operation**
*Demonstrates advanced thresholding with three output levels*
![Screenshot 2024-05-27 005009](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/e2206e25-d98f-43e0-8c33-7d69836442f5)

**Image Blurring (Mean Filter)**
*Shows noise reduction using mean filtering technique*
![Screenshot 2024-05-27 005059](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/a24e3787-2958-462c-98cf-fd961b54ffb5)

**Morphological Operations - Erosion**
*Binary image processing for shape analysis*
![Screenshot 2024-05-27 005406](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/26fbc857-9745-453f-95be-57d05a430ca7)

**Noise Addition**
*Adding salt and pepper noise for filter testing*
![Screenshot 2024-05-27 005810](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/00ca2407-9a25-4406-8c74-3d54d2dce3c8)

**Noise Removal**
*Effective noise reduction using median filter*
![Screenshot 2024-05-27 005825](https://github.com/haydarkadioglu/simple-image-processing-application/assets/95019347/73f3223a-ad35-442f-98c1-b276fa575a2c)

## 🛠️ Technical Implementation

### Core Technologies
- **Python 3.7+**: Modern Python development
- **NumPy**: Mathematical operations and array processing
- **PyQt5**: Cross-platform GUI framework
- **Matplotlib**: Histogram visualization
- **OpenCV**: Basic image I/O operations

### Architecture
```
sipa/
├── core/           # Image processing algorithms
│   ├── colors.py      # Color space conversions
│   ├── filters.py     # Filtering operations
│   ├── histogram.py   # Histogram & morphology
│   ├── rotate.py      # Geometric transformations
│   └── arithmetic.py  # Image arithmetic
├── gui/            # User interface
│   ├── main_window.py # Main application window
│   └── ui_main_window.py # Qt Designer UI file
└── main.py         # Application entry point
```

## 🎓 Educational Value

### Learning Objectives
- **Algorithm Understanding**: See how image processing works under the hood
- **NumPy Mastery**: Advanced array manipulation techniques
- **Computer Vision Basics**: Fundamental concepts in image analysis
- **GUI Development**: PyQt5 application structure

### Suitable For
- Computer Science students
- Image processing beginners
- Python developers
- Educators and researchers

## 🔧 Development

### Setting up Development Environment
```bash
git clone https://github.com/haydarkadioglu/simple-image-processing-application.git
cd simple-image-processing-application
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
python examples/basic_usage.py
```

### Building Distribution
```bash
python -m build
```

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- 512 MB RAM minimum
- 100 MB disk space
- Windows, macOS, or Linux

### Dependencies
- numpy >= 1.19.0
- matplotlib >= 3.3.0
- PyQt5 >= 5.15.0
- opencv-python >= 4.5.0

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

### Development Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Haydar Kadıoğlu**
- GitHub: [@haydarkadioglu](https://github.com/haydarkadioglu)
- Email: haydarkadioglu@example.com

## 🙏 Acknowledgments

- Educational image processing community
- NumPy development team
- PyQt5 framework contributors
- Computer vision researchers and educators

## 📈 Future Enhancements

- [ ] Advanced filtering techniques (Gaussian, Laplacian)
- [ ] More geometric transformations (affine, perspective)
- [ ] Color space conversions (HSV, LAB)
- [ ] Frequency domain operations (FFT)
- [ ] Machine learning integration
- [ ] Real-time image processing
- [ ] Plugin architecture

---

*This project is designed for educational purposes to help understand fundamental image processing concepts through hands-on implementation.*






