import tensorflow as tf
import numpy as np

MODEL_PATH = "models/CRNN_Model.keras"

class SoundModel:
    def __init__(self):
        self.model = tf.keras.models.load_model(MODEL_PATH)

    def predict(self, features: np.ndarray):
        """
        features shape: (1, time, freq) atau sesuai model kamu
        """
        preds = self.model.predict(features)
        return preds
