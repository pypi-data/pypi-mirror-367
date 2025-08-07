import cv2
import numpy as np
from .utils import plot_images

class FilterOperators:
    def __init__(self, img):
        self.img = img

    def sharpen(self):
        kernel = np.array([[0, -1, 0],
                           [-1, 5,-1],
                           [0, -1, 0]])
        result = cv2.filter2D(self.img, -1, kernel)
        plot_images([self.img, result], ['Original', 'Sharpened'])

    def high_pass(self):
        kernel = np.array([[-1, -1, -1],
                           [-1, 8, -1],
                           [-1, -1, -1]])
        result = cv2.filter2D(self.img, -1, kernel)
        plot_images([self.img, result], ['Original', 'High Pass'])
