import tensorflow as tf
import numpy as np
from utils import load_tiff_image

model = tf.keras.models.load_model("mangrove_classifier.h5")

def verify_image(path):
    img = load_tiff_image(path)
    img = np.expand_dims(img, axis=0) / 255.0

    prediction = model.predict(img)[0][0]

    if prediction > 0.5:
        return "Verified", float(prediction)
    else:
        return "Needs Review", float(1 - prediction)