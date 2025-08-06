import numpy as np


class Aritmatich:
    """
    Arithmetic operations between images.
    """

    @staticmethod
    def add_weighted(image1, alpha, image2, beta):
        """
        Add two images with weights.
        
        Args:
            image1 (numpy.ndarray): First image array
            alpha (float): Weight for first image
            image2 (numpy.ndarray): Second image array
            beta (float): Weight for second image
            
        Returns:
            numpy.ndarray: Weighted sum of images
        """
        if image1.shape != image2.shape:
            image2 = np.resize(image2, (image1.shape[0], image1.shape[1], 3))

        weighted_sum = ((alpha * image1) + (beta * image2)).astype(np.uint8)
        
        return weighted_sum
    
    @staticmethod
    def divide(image1, image2):
        """
        Divide first image by second image.
        
        Args:
            image1 (numpy.ndarray): Dividend image array
            image2 (numpy.ndarray): Divisor image array
            
        Returns:
            numpy.ndarray: Division result image array
        """
        if image1.shape != image2.shape:
            image2 = np.resize(image2, (image1.shape[0], image1.shape[1], 3))
            
        height, width, channels = image1.shape        
        image = np.zeros((height, width, channels), dtype=np.uint8)

        # Avoid division by zero
        image2_safe = np.where(image2 == 0, 1, image2)
        image = image1 / image2_safe

        return image.astype(np.uint8)
