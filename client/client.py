import requests
import time
from enum import Enum


BASE_URL = "http://127.0.0.1:5000"


class Status(Enum):
    """
    Enum for the status of the job.

    STATUS.COMPLETED if job completed successfully,
    STATUS.PENDING if job is still pending,
    STATUS.ERROR if exceeded max retries,
    STATUS.TIMEOUT if exceeded max time.
    """

    COMPLETED = "completed"
    PENDING = "pending"
    ERROR = "error"
    TIMEOUT = "timeout"


class StatusClient:
    class Stats:
        """
        Stores statistics on client performance.

        Attributes:
            total_jobs (int): The total number of jobs submitted.
            total_requests (int): The total number of requests made to the server.
            total_lag (float): The total time (in seconds) of lag between server completion and wait_complete.
        """

        def __init__(self):
            self.total_jobs: int = 0
            self.total_requests: int = 0
            self.total_lag: float = 0

        def __str__(self):
            return (
                f"Client Performance Statistics:\n"
                f"  Total Jobs Submitted : {self.total_jobs}\n"
                f"  Total Requests Made  : {self.total_requests}\n"
                f"  Total Lag (seconds)  : {self.total_lag:.10f}"
            )

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

    def __init__(self, enable_logs: bool = True) -> None:
        self.stats: StatusClient.Stats = StatusClient.Stats()
        self.enable_logs = enable_logs

    def get_statistics(self) -> Stats:
        """
        Get statistics on client performance
        """
        return self.stats

    def submit_job(self) -> None:
        """
        Start a new job on the server.
        """
        self.stats.total_jobs += 1
        response = requests.post(f"{BASE_URL}/start")
        if response.status_code == 202:
            self._log(f"Job started successfully")
        else:
            self._log(f"Failed to start the job: {response.text}")

    def get_status(self) -> Status:
        """
        Get the current status of the job.

        Returns:
            Status: The final status on return.
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
                    STATUS.COMPLETED if job completed successfully,
                    STATUS.ERROR if exceeded max retries,
                    STATUS.TIMEOUT if exceeded max time.
        """
        if args is None:
            args = StatusClient.WaitArgs()

        start_time = time.time()
        interval = args.check_interval  # Start with 1 second
        tries = 0
        while tries < args.retry:
            while time.time() - start_time < args.timeout:
                response = self._request_video()
                result = response["result"]
                if result == "completed":
                    lag = time.time() - response["_completion_time"]
                    self._log(
                        f"Job completed. Lag: {lag:.2f} seconds, Total Jobs: {self.stats.total_jobs}, Total Requests: {self.stats.total_requests}"
                    )
                    self.stats.total_lag += lag
                    return Status.COMPLETED
                elif result == "error":
                    tries += 1
                    break
                time.sleep(interval)

                self._log(f"Checked status and got response: {response}. Retrying")
                if args.backoff:
                    interval = min(interval * 2, 10)

            if tries < args.retry:
                self._log(f"Checked status and got response: {response}. Retrying with new job")
                interval = args.check_interval
                self.submit_job()

        if time.time() - start_time >= args.timeout:
            self._log("Timeout exceeded.")
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
            self._log(f"Error while checking the status: {e}")
            return None

    def _log(self, message: str) -> None:
        """
        Print a message if logging is enabled.
        """
        if self.enable_logs:
            print("[StatusClient] ", message)


if __name__ == "__main__":
    # Start the job
    client = StatusClient()
    client.submit_job()
    end_status = client.wait_complete(StatusClient.WaitArgs())
    print(f"Wait finished with status: {end_status}")
    print(client.stats)
