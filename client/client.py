import requests
import time
import types
import json

BASE_URL = "http://127.0.0.1:5000"


class VideoClient:
    class Stats:
        def __init__(self):
            self.total_jobs: int = 0
            self.total_requests: int = 0
            self.total_lag: float = 0

        def __str__(self):
            return (
                f"Stats: {self.total_jobs} jobs, {self.total_requests} requests, {self.total_lag:.10f} seconds of lag"
            )

    def __init__(self) -> None:
        self.stats: VideoClient.Stats = VideoClient.Stats()

    def get_statistics(self) -> Stats:
        return self.stats

    def submit_job(self) -> dict:
        """Send a POST request to start the job."""
        self.stats.total_jobs += 1
        response = requests.post(f"{BASE_URL}/start")
        if response.status_code == 202:
            print("Job started successfully:", response.json())
            return response.json()
        else:
            print("Failed to start the job:", response.text)
            return response.json()

    def try_get_video(self) -> dict:
        """Send a Get"""
        try:
            self.stats.total_requests += 1
            response = requests.get(f"{BASE_URL}/status")
            return response.json()
        except Exception as e:
            print("Error while checking the status:", e)
            return None

    def get_video(self, timeout=180) -> str:
        """
        Block and poll the server until the job completes, times out, or errors.

        Implements a backoff mechanism for polling intervals.
        Args:
            timeout (int): Maximum time to wait (in seconds).
        Returns:
            str: The final status ("completed", "error") or "timeout".
        """
        start_time = time.time()
        interval = 1  # Start with 1 second

        while time.time() - start_time < timeout:
            response = self.try_get_video()
            result = response["result"]
            print(response)
            if result == "completed":
                print(time.time() - response["_completion_time"])
                self.stats.total_lag += time.time() - response["_completion_time"]
                return response
            elif result == "error":
                return response

            time.sleep(interval)
            interval = min(interval * 2, 10)

        return "timeout"


if __name__ == "__main__":
    # Start the job
    client = VideoClient()

    client.submit_job()
    client.get_video()
    print(client.stats)
