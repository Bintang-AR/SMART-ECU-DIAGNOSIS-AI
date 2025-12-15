import tensorflow as tf
import numpy as np

MODEL_PATH = "models/CRNN_Model.keras"

class SoundModel:
    def __init__(self):
        self.model = tf.keras.models.load_model(MODEL_PATH, compile=False)

    def predict(self, features: np.ndarray):
        preds = self.model.predict(features, verbose=0)
        return preds
