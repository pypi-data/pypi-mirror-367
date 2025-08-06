import numpy as np


class Histogram:
    """
    Histogram operations and morphological transformations.
    """

    @staticmethod
    def histogram_stretching(image):
        """
        Stretch histogram to full intensity range.
        
        Args:
            image (numpy.ndarray): Input image array
            
        Returns:
            numpy.ndarray: Histogram-stretched image array
        """
        image = image.astype(np.float32)

        min_val = np.min(image)
        max_val = np.max(image)

        stretched_image = 255 * (image - min_val) / (max_val - min_val)
        stretched_image = stretched_image.astype(np.uint8)

        return stretched_image
    
    @staticmethod
    def histogram_equalization(image):
        """
        Perform histogram equalization to improve contrast.
        
        Args:
            image (numpy.ndarray): Input image array
            
        Returns:
            numpy.ndarray: Histogram-equalized image array
        """
        gray_image = np.mean(image, axis=2, dtype=np.uint8) 

        height, width = gray_image.shape

        histogram = np.zeros(256, dtype=int)
        for y in range(height):
            for x in range(width):
                intensity = gray_image[y, x]
                histogram[intensity] += 1

        histogram_normalized = histogram / (height * width)
        cdf = np.cumsum(histogram_normalized)

        equalized_image = np.zeros_like(gray_image)
        for y in range(height):
            for x in range(width):
                intensity = gray_image[y, x]
                equalized_intensity = np.round(255 * cdf[intensity]).astype(int)
                equalized_image[y, x] = equalized_intensity

        return equalized_image
    
    @staticmethod
    def calculate_gray_histogram(image):
        """
        Calculate histogram of grayscale image.
        
        Args:
            image (numpy.ndarray): Grayscale image array
            
        Returns:
            numpy.ndarray: Histogram array
        """
        histogram = np.zeros(256, dtype=int)
        
        for pixel_value in image.flatten():
            histogram[pixel_value] += 1

        return histogram

    @staticmethod
    def calculate_rgb_histogram(image):
        """
        Calculate histograms for RGB channels.
        
        Args:
            image (numpy.ndarray): RGB image array
            
        Returns:
            tuple: RGB histograms (r_histogram, g_histogram, b_histogram)
        """
        r_histogram = np.zeros(256, dtype=int)
        g_histogram = np.zeros(256, dtype=int)
        b_histogram = np.zeros(256, dtype=int)
        
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                b, g, r = image[y, x]
                r_histogram[r] += 1
                g_histogram[g] += 1
                b_histogram[b] += 1
        
        return r_histogram, g_histogram, b_histogram

    @staticmethod
    def dilate(image, kernel_size):
        """
        Perform morphological dilation.
        
        Args:
            image (numpy.ndarray): Binary image array
            kernel_size (int): Size of structuring element
            
        Returns:
            numpy.ndarray: Dilated image array
        """
        kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
        dilated_image = np.zeros_like(image)
        image_height, image_width = image.shape
        kernel_height, kernel_width = kernel.shape

        padding_vertical = kernel_height // 2
        padding_horizontal = kernel_width // 2
        padded_image = np.pad(image, ((padding_vertical, padding_vertical), (padding_horizontal, padding_horizontal)), mode='constant')

        for y in range(image_height):
            for x in range(image_width):
                region = padded_image[y:y+kernel_height, x:x+kernel_width]
                dilated_image[y, x] = np.max(region * kernel)

        return dilated_image

    @staticmethod
    def erode(image, kernel_size):
        """
        Perform morphological erosion.
        
        Args:
            image (numpy.ndarray): Binary image array
            kernel_size (int): Size of structuring element
            
        Returns:
            numpy.ndarray: Eroded image array
        """
        kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
        eroded_image = np.zeros_like(image)
        image_height, image_width = image.shape
        kernel_height, kernel_width = kernel.shape

        padding_vertical = kernel_height // 2
        padding_horizontal = kernel_width // 2
        padded_image = np.pad(image, ((padding_vertical, padding_vertical), (padding_horizontal, padding_horizontal)), mode='constant')

        for y in range(image_height):
            for x in range(image_width):
                region = padded_image[y:y+kernel_height, x:x+kernel_width]
                eroded_image[y, x] = np.min(region * kernel)

        return eroded_image

    @staticmethod
    def opening(image, kernel):
        """
        Perform morphological opening (erosion followed by dilation).
        
        Args:
            image (numpy.ndarray): Binary image array
            kernel (int): Size of structuring element
            
        Returns:
            numpy.ndarray: Opened image array
        """
        return Histogram.dilate(Histogram.erode(image, kernel), kernel)

    @staticmethod
    def closing(image, kernel):
        """
        Perform morphological closing (dilation followed by erosion).
        
        Args:
            image (numpy.ndarray): Binary image array
            kernel (int): Size of structuring element
            
        Returns:
            numpy.ndarray: Closed image array
        """
        return Histogram.erode(Histogram.dilate(image, kernel), kernel)
