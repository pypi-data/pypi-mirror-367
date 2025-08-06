import numpy as np

class Histogram:


    def histogram_stretching(image):

        image = image.astype(np.float32)

        min_val = np.min(image)
        max_val = np.max(image)

        stretched_image = 255 * (image - min_val) / (max_val - min_val)
        stretched_image = stretched_image.astype(np.uint8)

        return stretched_image
    
    def histogram_equalization(image):

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
    
    def calculate_gray_histogram(image):

        histogram = np.zeros(256, dtype=int)
        

        for pixel_value in image.flatten():
            histogram[pixel_value] += 1

        return histogram

    def calculate_rgb_histogram(image):
        r_histogram = np.zeros(256, dtype=int)
        g_histogram = np.zeros(256, dtype=int)
        b_histogram = np.zeros(256, dtype=int)
        
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                b,g,r = image[y, x]
                r_histogram[r] += 1
                g_histogram[g] += 1
                b_histogram[b] += 1
        
        return r_histogram, g_histogram, b_histogram



    def dilate(image, kernel_size):
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

    def erode(image, kernel_size):
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

    def opening(image, kernel):
        return Histogram.dilate(Histogram.erode(image, kernel), kernel)

    def closing(image, kernel):
        return Histogram.erode(Histogram.dilate(image, kernel), kernel)