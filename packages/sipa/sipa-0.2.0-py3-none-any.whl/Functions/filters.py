import numpy as np

class Filters:


    def unsharp_mask(image, kernel_size=5, amount=0.1):


        if len(image.shape) == 2:
            image = np.stack((image,)*3, axis=-1)


        blurred = np.zeros_like(image)
        
        blurred = Filters.mean_filter(image, int(kernel_size))


        sharpened = np.clip(image + amount * (image - blurred), 0, 255)


        return sharpened.astype(np.uint8)


  
    def mean_filter(image, matrix_size):

        kernel = np.ones((matrix_size, matrix_size), dtype=np.float32) / (matrix_size*matrix_size)

        filtered_image = Filters.convolve(image, kernel)

        return filtered_image
    
    
    def median_filter(image, kernel_size):
        
        if len(image.shape) == 3:
            return Filters.median_filterRGB(image,kernel_size)

        height, width = image.shape[:2]
        filtered_image = np.zeros_like(image)
        padding = kernel_size // 2

        for y in range(padding, height - padding):
            for x in range(padding, width - padding):

                window = image[y - padding:y + padding + 1, x - padding:x + padding + 1]

                filtered_image[y, x] = np.median(window)

        return filtered_image
    
    def median_filterRGB(image, kernel_size):
        
        height, width, num_channels = image.shape
        filtered_image = np.zeros_like(image)
        padding = kernel_size // 2

        for c in range(num_channels):
            for y in range(padding, height - padding):
                for x in range(padding, width - padding):

                    window = image[y - padding:y + padding + 1, x - padding:x + padding + 1, c]

                    filtered_image[y, x, c] = np.median(window)

        return filtered_image

    

    def salt_pepper(image, nums):

        if len(image.shape) == 3:
            return Filters.salt_pepperRGB(image, nums)

        height, width = image.shape[:2]
        noisy = np.copy(image)
        rows = np.random.randint(0,height, nums)
        cols = np.random.randint(0,width, nums)

        for i in range(nums):
            if i % 2 == 1:
                noisy[rows[i], cols[i]] = 255
            else: 
                noisy[rows[i], cols[i]] = 0
        
        return noisy
    
    
    def salt_pepperRGB(image, nums):

        height, width = image.shape[:2]
        noisy = np.copy(image)
        rows = np.random.randint(0,height, nums)
        cols = np.random.randint(0,width, nums)

        for i in range(nums):
            if i % 2 == 1:
                noisy[rows[i], cols[i], : ] = 255
            else: 
                noisy[rows[i], cols[i], : ] = 0
        
        return noisy

    def detect_edge_prewitt(image):
        kernel_x = np.array([[-1,0,1],
                             [-1,0,1],
                             [-1,0,1]])
        
        kernel_y = np.array([[-1,-1,-1],
                             [0,0,0],
                             [1,1,1]])
        
        edge_x = Filters.convolve(image, kernel_x)
        edge_y = Filters.convolve(image, kernel_y)

        edges = Filters.add_weighted(edge_x, 0.5, edge_y, 0.5,0)

        return edges





    

    def convolve(image, kernel):

        if len(image.shape) == 3:
            return Filters.convolveRGB(image,kernel)
        image_height, image_width = image.shape[:2]
        kernel_height, kernel_width = kernel.shape


        padding_vertical = kernel_height // 2
        padding_horizontal = kernel_width // 2


        padded_image = np.pad(image, ((padding_vertical, padding_vertical), (padding_horizontal, padding_horizontal)), mode='constant')


        
        result = np.zeros_like(image)


        for y in range(image_height):
            for x in range(image_width):

                region = padded_image[y:y+kernel_height, x:x+kernel_width]

                result[y, x] = np.sum(region * kernel)

        return result
    def convolveRGB(image, kernel):
        image_height, image_width, num_channels = image.shape
        kernel_height, kernel_width = kernel.shape


        padding_vertical = kernel_height // 2
        padding_horizontal = kernel_width // 2
        padded_image = np.pad(image, ((padding_vertical, padding_vertical), (padding_horizontal, padding_horizontal), (0, 0)), mode='constant')


        result = np.zeros_like(image)


        for c in range(num_channels):
            for y in range(image_height):
                for x in range(image_width):

                    result[y, x, c] = np.sum(padded_image[y:y+kernel_height, x:x+kernel_width, c] * kernel)

        return result

    
    def add_weighted(image1, alpha, image2, beta, gamma):

        weighted_sum = (alpha * image1 + beta * image2 + gamma).astype(np.uint8)

        weighted_sum = np.clip(weighted_sum, 0, 255)
        return weighted_sum