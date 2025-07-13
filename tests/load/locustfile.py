# tests/load/locustfile.py

from locust import HttpUser, task, between

class FluxPilotUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def generate(self):
        payload = {"prompt": "Load testing prompt", "max_new_tokens": 20}
        self.client.post("/generate", json=payload, timeout=60)
