import numpy as np


class Colors:



    def convert_to_gray(image):
    
        height, width, _ = image.shape
        
        gray_image = np.zeros((height, width), dtype=np.uint8)

        
        gray_image[:,:] = (0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]).astype(np.uint8)
        
        return gray_image

    def convert_to_binary(image, value):

        binary_image = np.zeros_like(image, dtype=np.uint8)
        binary_image[image > value] = 255
        binary_image[image < value] = 0

        return binary_image

    
    def rgb_transformation(image, b=0, g=0, r=0):
        height, width, channels = image.shape
        transformed_image = np.zeros((height, width, channels), dtype=np.uint8)

        transformed_image[:,:,:] = np.minimum(image[:,:,:] + [r,g,b], 255)


        return transformed_image
    
    
    def increase_contrast(image, factor:float):
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
    
    
    def calculate_mean(image, channels:int = 1):

        height, width = image.shape[:2]
        

        total_sum = np.sum(image)
        

        total_pixels = height * width * channels
        

        mean_value = total_sum / total_pixels
        
        return mean_value


    def single_threshold(image, threshold_value):

        binary_image = np.zeros_like(image, dtype=np.uint8)
        binary_image[image > threshold_value] = 255
        binary_image[image < threshold_value] = 0


        return binary_image

    def double_threshold(image, low_threshold, high_threshold, interValue=127):


        binary_image = np.zeros_like(image, dtype=np.uint8)
        binary_image[image > high_threshold] = 255
        binary_image[(image > low_threshold) & (image <= high_threshold)] = interValue  # İki eşik arasında kalanlar için 128 değerini atadım
        binary_image[image <= low_threshold] = 0

        return binary_image

