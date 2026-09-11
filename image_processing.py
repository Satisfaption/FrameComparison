import cv2
import numpy as np


def extract_shape_mask(img_bgr):
    """Generates a solid binary mask using HSV saturation thresholding."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    _, binary_mask = cv2.threshold(saturation, 4, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    return cv2.dilate(binary_mask, kernel, iterations=1)


def compare_frames(search_bgr, template_mask):
    """Compares current frame mask against template mask and returns confidence score."""
    search_mask = extract_shape_mask(search_bgr)
    result = cv2.matchTemplate(search_mask, template_mask, cv2.TM_CCOEFF_NORMED)
    _, confidence, _, _ = cv2.minMaxLoc(result)
    return confidence