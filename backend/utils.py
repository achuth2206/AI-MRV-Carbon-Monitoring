import cv2
import numpy as np

def load_tiff_image(path, target_size=(128,128)):

    # Read image
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError(f"Could not read image: {path}")

    # If grayscale → convert to RGB
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # If more than 3 channels → keep first 3
    if len(img.shape) == 3 and img.shape[2] > 3:
        img = img[:, :, :3]

    # Resize
    img = cv2.resize(img, target_size)

    return img