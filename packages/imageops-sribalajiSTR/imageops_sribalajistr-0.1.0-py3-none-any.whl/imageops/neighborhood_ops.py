import cv2
import numpy as np
from .utils import plot_images

class NeighborhoodOperators:
    def __init__(self, img):
        self.img = img

    def mean_filter(self):
        result = cv2.blur(self.img, (3, 3))
        plot_images([self.img, result], ['Original', 'Mean Filter'])

    def median_filter(self):
        result = cv2.medianBlur(self.img, 3)
        plot_images([self.img, result], ['Original', 'Median Filter'])

    def gaussian_filter(self):
        result = cv2.GaussianBlur(self.img, (5, 5), 0)
        plot_images([self.img, result], ['Original', 'Gaussian Filter'])
