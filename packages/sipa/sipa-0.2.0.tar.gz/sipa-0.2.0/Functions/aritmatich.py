import numpy as np


class Aritmatich:
    
    

    def add_weighted(image1, alpha, image2, beta):

        cur = np.zeros((image1.shape[0], image1.shape[1], 3), np.uint8)
        
        if image1.shape != image2.shape:
            image2 = np.resize(image2,(image1.shape[0], image1.shape[1], 3))

        

        weighted_sum = ((alpha * image1) + (beta * image2) ).astype(np.uint8)
        
        
        
        return weighted_sum
    


    
    def divide(image1, image2):
        
        
        if image1.shape != image2.shape:
            image2 = np.resize(image2,(image1.shape[0], image1.shape[1], 3))
        height, width,channels = image1.shape        
        image = np.zeros((height, width, channels),dtype=np.uint8)

        image = image1/image2

        return image