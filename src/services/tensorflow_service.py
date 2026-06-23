import cv2
import numpy as np

import tensorflow as tf

from config.settings import MODEL_PATH
from config.class_names import (
    CLASS_NAMES,
    EXPECTED_CLASSES
)


class TensorflowService:

    def __init__(self):
        self.model = tf.keras.models.load_model(MODEL_PATH)

        model_classes = self.model.output_shape[-1]

        if model_classes != EXPECTED_CLASSES:
            raise ValueError(
                f"El modelo espera {model_classes} clases "
                f"pero CLASS_NAMES tiene "
                f"{EXPECTED_CLASSES}."
            )

    def preprocess(self, frame):

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mask = cv2.inRange(
            img_rgb,
            (180, 180, 180),
            (255, 255, 255)
        )

        img_rgb[mask == 255] = (255, 255, 255)

        img_rgb = cv2.convertScaleAbs(
            img_rgb,
            alpha=1.2,
            beta=10
        )

        img_resized = cv2.resize(img_rgb, (100, 100))

        return np.expand_dims(
            img_resized / 255.0,
            axis=0
        )

    def predict(self, frame):

        img_array = self.preprocess(frame)

        predictions = self.model.predict(
            img_array,
            verbose=0
        )

        index = np.argmax(predictions)

        if index >= len(CLASS_NAMES):
            return "unknown"

        return CLASS_NAMES[index]