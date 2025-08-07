import cv2
from .utils import plot_images

class HistogramOperators:
    def __init__(self, img):
        self.img = img

    def equalize(self):
        result = cv2.equalizeHist(self.img)
        plot_images([self.img, result], ['Original', 'Equalized'])
