import numpy as np


class Rotate:
    """
    Image geometric transformations including rotation, cropping, and zooming.
    """
    
    @staticmethod
    def rotate_image(image):
        """
        Rotate image 90 degrees clockwise.
        
        Args:
            image (numpy.ndarray): Input image array
            
        Returns:
            numpy.ndarray: Rotated image array
        """
        if len(image.shape) == 3:
            height, width, channels = image.shape
            cur = np.zeros((width, height, channels), dtype=np.uint8)

            for i in range(width):
                for j in range(height):
                    cur[i, j, :] = image[j, width-i-1, :]
        else:
            height, width = image.shape[:2]
            cur = np.zeros((width, height), dtype=np.uint8)

            for i in range(width-1):
                for j in range(height-1):
                    cur[i, j] = image[j, width-i-1]

        return cur

    @staticmethod
    def crop(img, x1, y1, x2, y2):
        """
        Crop image to specified rectangle.
        
        Args:
            img (numpy.ndarray): Input image array
            x1 (int): Top-left x coordinate
            y1 (int): Top-left y coordinate
            x2 (int): Bottom-right x coordinate
            y2 (int): Bottom-right y coordinate
            
        Returns:
            numpy.ndarray: Cropped image array
        """
        height, width = x2-x1, y2-y1

        if len(img.shape) == 3:
            cropped_img = np.zeros((height, width, 3), dtype=np.uint8)
            cropped_img[:, :, :] = img[x1:x2, y1:y2, :] 
        else:
            cropped_img = np.zeros((height, width), dtype=np.uint8)
            cropped_img[:, :] = img[x1:x2, y1:y2]

        return cropped_img

    @staticmethod
    def zoom(image, factor):
        """
        Zoom image by specified factor.
        
        Args:
            image (numpy.ndarray): Input image array
            factor (float): Zoom factor
            
        Returns:
            numpy.ndarray: Zoomed image array
        """
        if len(image.shape) == 3:
            return Rotate.zoomRGB(image, factor)
            
        height, width = image.shape
        new_height = int(height * factor)
        new_width = int(width * factor)
        new_image = np.zeros((new_height, new_width), dtype=np.uint8)
        
        for i in range(new_height):
            for j in range(new_width):
                new_image[i, j] = image[int(i / factor), int(j / factor)]
        
        return new_image

    @staticmethod
    def zoomRGB(image, factor):
        """
        Zoom RGB image by specified factor.
        
        Args:
            image (numpy.ndarray): RGB image array
            factor (float): Zoom factor
            
        Returns:
            numpy.ndarray: Zoomed RGB image array
        """
        height, width, channel = image.shape
        height = int(height * factor)
        width = int(width * factor)
        new_image = np.zeros((height, width, channel), dtype=np.uint8)
        
        for i in range(height):
            for j in range(width):
                for x in range(channel):
                    new_image[i, j, x] = image[int(i/factor), int(j/factor), x]

        return new_image
