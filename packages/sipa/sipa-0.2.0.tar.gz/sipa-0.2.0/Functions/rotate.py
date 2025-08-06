import numpy as np


class Rotate:
    def rotate_image(image):

        if len(image.shape) == 3:
            height, width, channels = image.shape

            cur = np.zeros((width, height, channels), dtype=np.uint8)


            for i in range(width):
                for j in range(height):
                    
                    cur[i,j, :] = image[j,width-i-1, :]
        else:
            height, width = image.shape[:2]
            
            cur = np.zeros((width, height), dtype=np.uint8)

            for i in range(width-1):
                for j in range(height-1):
                    
                    cur[i,j] = image[j,width-i-1]

        return cur

                    

    def crop(img, x1,y1,x2,y2):
        height, width = x2-x1,y2-y1

        if len(img.shape) == 3:
            cropped_img = np.zeros((height, width, 3), dtype=np.uint8)
            cropped_img[:,:, :] = img[x1:x2,y1:y2, :] 

        else:
            cropped_img = np.zeros((height, width), dtype=np.uint8)
            cropped_img[:,:] = img[x1:x2,y1:y2]

        return cropped_img

    def zoom(image, factor):

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


    def zoomRGB(image, factor):
        new_image = None
        
        height, width, channel = image.shape
        height = int(height*factor)
        width = int(width*factor)
        new_image = np.zeros((height,width, channel),dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                for x in range(channel):
                    new_image[i,j, x] = image[int(i/factor), int(j/factor),x]

        return new_image
    