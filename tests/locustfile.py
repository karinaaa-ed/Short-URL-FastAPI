from locust import HttpUser, task, between
import random


class ShortUrlUser(HttpUser):
    wait_time = between(0.5, 2.5)

    def on_start(self):
        # Авторизация
        auth = self.client.post("/auth/jwt/login", data={
            "username": "test@example.com",
            "password": "testpass",
        })
        self.token = auth.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def create_link(self):
        self.client.post(
            "/links/shorten",
            json={"original_url": f"https://example.com/{random.randint(1, 100000)}"},
            headers=self.headers
        )

    @task(10)
    def redirect_link(self):
        self.client.get(f"/links/test{random.randint(1, 100)}")