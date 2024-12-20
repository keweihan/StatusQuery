import requests
import time

BASE_URL = "http://127.0.0.1:5000"


class VideoClient:
    def __init__(self):
        pass

    def submit_job(self):
        """Send a POST request to start the job."""
        try:
            response = requests.post(f"{BASE_URL}/start")
            if response.status_code == 202:
                print("Job started successfully:", response.json())
            else:
                print("Failed to start the job:", response.text)
        except Exception as e:
            print("Error while starting the job:", e)

    def get_video(self):
        """Send a Get"""
        try:
            response = requests.get(f"{BASE_URL}/status")
            if response.status_code == 200:
                return response.json()["result"]
            else:
                print("Failed to get status:", response.text)
        except Exception as e:
            print("Error while checking the status:", e)
            return None


if __name__ == "__main__":
    # Start the job
    client = VideoClient()

    client.submit_job()
    time.sleep(10)
    client.get_video()
