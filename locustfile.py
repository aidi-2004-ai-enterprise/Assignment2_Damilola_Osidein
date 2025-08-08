from locust import HttpUser, task, between
import random

class PenguinUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    @task
    def predict(self):
        # Generate random penguin data within realistic ranges
        data = {
            "bill_length_mm": random.uniform(30, 60),
            "bill_depth_mm": random.uniform(10, 20),
            "flipper_length_mm": random.uniform(170, 230),
            "body_mass_g": random.uniform(2700, 6300)
        }
        # Send POST request to /predict endpoint
        self.client.post("/predict", json=data)