import numpy as np

def generate_vibration_data(length: int = 200):
    data = []
    for i in range(length):
        data.append({
            "time": round(i * 0.01, 4),
            "amplitude": float(np.sin(i * 0.1) + np.random.rand() * 0.3),
            "frequency": float(50 + np.sin(i * 0.05) * 40)
        })
    return data