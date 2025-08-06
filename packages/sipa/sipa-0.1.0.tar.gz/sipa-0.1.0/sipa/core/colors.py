import numpy as np


class Colors:
    """
    Color manipulation and conversion operations for images.
    """

    @staticmethod
    def convert_to_gray(image):
        """
        Convert RGB image to grayscale using luminance formula.
        
        Args:
            image (numpy.ndarray): RGB image array
            
        Returns:
            numpy.ndarray: Grayscale image array
        """
        height, width, _ = image.shape
        
        gray_image = np.zeros((height, width), dtype=np.uint8)

        gray_image[:,:] = (0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]).astype(np.uint8)
        
        return gray_image

    @staticmethod
    def convert_to_binary(image, value):
        """
        Convert grayscale image to binary using threshold value.
        
        Args:
            image (numpy.ndarray): Grayscale image array
            value (int): Threshold value
            
        Returns:
            numpy.ndarray: Binary image array
        """
        binary_image = np.zeros_like(image, dtype=np.uint8)
        binary_image[image > value] = 255
        binary_image[image < value] = 0

        return binary_image

    @staticmethod
    def rgb_transformation(image, b=0, g=0, r=0):
        """
        Apply RGB transformation by adding values to each channel.
        
        Args:
            image (numpy.ndarray): RGB image array
            b (int): Blue channel offset
            g (int): Green channel offset
            r (int): Red channel offset
            
        Returns:
            numpy.ndarray: Transformed image array
        """
        height, width, channels = image.shape
        transformed_image = np.zeros((height, width, channels), dtype=np.uint8)

        transformed_image[:,:,:] = np.minimum(image[:,:,:] + [r,g,b], 255)

        return transformed_image
    
    @staticmethod
    def increase_contrast(image, factor: float):
        """
        Increase image contrast by specified factor.
        
        Args:
            image (numpy.ndarray): Input image array
            factor (float): Contrast factor
            
        Returns:
            numpy.ndarray: Contrast-enhanced image array
        """
        increased_contrast_image = np.copy(image)
        if len(image.shape) == 3:
            for c in range(3):  
                channel = image[:, :, c]
                mean_value = np.mean(channel)
                increased_contrast_channel = (channel - mean_value) * factor + mean_value
                increased_contrast_image[:, :, c] = np.clip(increased_contrast_channel, 0, 255)
        else:
            increased_contrast_image = (image - Colors.calculate_mean(image)) * factor + Colors.calculate_mean(image)
            increased_contrast_image = np.clip(increased_contrast_image, 0, 255)

        return increased_contrast_image.astype(np.uint8)
    
    @staticmethod
    def calculate_mean(image, channels: int = 1):
        """
        Calculate mean value of image.
        
        Args:
            image (numpy.ndarray): Input image array
            channels (int): Number of channels
            
        Returns:
            float: Mean value
        """
        height, width = image.shape[:2]
        total_sum = np.sum(image)
        total_pixels = height * width * channels
        mean_value = total_sum / total_pixels
        
        return mean_value

    @staticmethod
    def single_threshold(image, threshold_value):
        """
        Apply single threshold to create binary image.
        
        Args:
            image (numpy.ndarray): Grayscale image array
            threshold_value (int): Threshold value
            
        Returns:
            numpy.ndarray: Binary image array
        """
        binary_image = np.zeros_like(image, dtype=np.uint8)
        binary_image[image > threshold_value] = 255
        binary_image[image < threshold_value] = 0

        return binary_image

    @staticmethod
    def double_threshold(image, low_threshold, high_threshold, interValue=127):
        """
        Apply double threshold with three output levels.
        
        Args:
            image (numpy.ndarray): Grayscale image array
            low_threshold (int): Lower threshold value
            high_threshold (int): Higher threshold value
            interValue (int): Intermediate value for pixels between thresholds
            
        Returns:
            numpy.ndarray: Triple-level image array
        """
        binary_image = np.zeros_like(image, dtype=np.uint8)
        binary_image[image > high_threshold] = 255
        binary_image[(image > low_threshold) & (image <= high_threshold)] = interValue
        binary_image[image <= low_threshold] = 0

        return binary_image
