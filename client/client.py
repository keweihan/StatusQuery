import requests
import time
from enum import Enum
from dataclasses import dataclass

BASE_URL = "http://127.0.0.1:5000"


class Status(Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    ERROR = "error"
    TIMEOUT = "timeout"


class StatusClient:
    class Stats:
        def __init__(self):
            self.total_jobs: int = 0
            self.total_requests: int = 0
            self.total_lag: float = 0

        def __str__(self):
            return f"Stats: {self.total_jobs} jobs, {self.total_requests} requests, {self.total_lag:.10f} seconds of lag between server completion and wait_complete"

    class WaitArgs:
        """
        A configuration class for specifying wait parameters.

        Attributes:
            check_interval (float): Initial interval (in seconds) between status checks.
            backoff (bool): If True, use exponential backoff strategy for polling intervals.
            timeout (int): The maximum time (in seconds) to wait for the operation to complete.
            retry (int): The number of retry attempts allowed in case of errors.
        """

        def __init__(self, check_interval: float = 1, backoff: bool = True, timeout: int = 180, retry: int = 3):
            self.check_interval = check_interval
            self.backoff = backoff
            self.timeout = timeout
            self.retry = retry

    def __init__(self) -> None:
        self.stats: StatusClient.Stats = StatusClient.Stats()

    def get_statistics(self) -> Stats:
        """
        Get statistics on client performance
        """
        return self.stats

    def submit_job(self) -> dict:
        """
        Start a new job.
        """
        self.stats.total_jobs += 1
        response = requests.post(f"{BASE_URL}/start")
        if response.status_code == 202:
            print("Job started successfully:", response.json())
            return response.json()
        else:
            print("Failed to start the job:", response.text)
            return response.json()

    def get_status(self) -> Status:
        """
        Get the current status of the job.
        """
        response = self._request_video()
        if response is None:
            return Status.ERROR

        result = response["result"]
        if result == "completed":
            return Status.COMPLETED
        elif result == "pending":
            return Status.PENDING
        elif result == "error":
            return Status.ERROR

    def wait_complete(
        self,
        args: WaitArgs = None,
    ) -> Status:
        """
        Block and poll the server until the job completes, times out, or errors.

        Args:
            args (WaitArgs): Configuration parameters for waiting.
        Returns:
            Status: The final status on return.
        """
        if args is None:
            args = StatusClient.WaitArgs()

        start_time = time.time()
        interval = args.check_interval  # Start with 1 second
        tries = 0
        while tries < args.retry and time.time() - start_time < args.timeout:
            response = self._request_video()
            result = response["result"]
            print(response)
            if result == "completed":
                print(time.time() - response["_completion_time"])
                self.stats.total_lag += time.time() - response["_completion_time"]
                return Status.COMPLETED
            elif result == "error":
                tries += 1
            time.sleep(interval)

            if args.backoff:
                interval = min(interval * 2, 10)

        if time.time() - start_time >= args.timeout:
            return Status.TIMEOUT
        else:
            return Status.ERROR

    def _request_video(self) -> dict:
        """
        Send request to check the status of the job.
        """
        try:
            self.stats.total_requests += 1
            response = requests.get(f"{BASE_URL}/status")
            return response.json()
        except requests.RequestException as e:
            print("Error while checking the status:", e)
            return None


if __name__ == "__main__":
    # Start the job
    client = StatusClient()
    client.submit_job()
    client.wait_complete(StatusClient.WaitArgs())
    client.get_status()
    print(client.stats)
