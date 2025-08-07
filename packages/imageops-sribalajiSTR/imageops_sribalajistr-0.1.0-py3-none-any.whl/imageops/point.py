import cv2
import numpy as np
from .utils import plot_images

class PointOperators:
    def __init__(self, img):
        self.img = img

    def negative_transformation(self):
        result = 255 - self.img
        plot_images([self.img, result], ['Original', 'Negative'])

    def log_transformation(self):
        img_float = self.img.astype(np.float32)
        c = 255 / np.log(1 + np.max(img_float))
        result = c * np.log(1 + img_float)
        result = np.uint8(result)
        plot_images([self.img, result], ['Original', 'Log'])

    def power_law_transformation(self, gamma=0.4):
        img_float = self.img / 255.0
        result = np.power(img_float, gamma)
        result = np.uint8(result * 255)
        plot_images([self.img, result], ['Original', f'Gamma={gamma}'])

    def all_transformations(self):
        self.negative_transformation()
        self.log_transformation()
        self.power_law_transformation()
