import subprocess
import time
import unittest
import requests
from client.client import StatusClient


class IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start the server before running tests."""
        cls.server_process = subprocess.Popen(
            ["python", "server/server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(1)  # Wait for the server to start
        print("[TEST]: Server started")

    @classmethod
    def tearDownClass(cls):
        """Terminate the server subprocess after tests are done."""
        cls.server_process.terminate()
        cls.server_process.wait()

        stdout, stderr = cls.server_process.communicate()
        print("\n========= Server Logs (stdout) =========\n", stdout.decode("utf-8"))
        print("\n========= Server Logs (stderr) =========\n", stderr.decode("utf-8"))

    def test_integration_smoke(self):
        """Test that the client interacts with the server and prints logs."""
        print("[TEST]: Client running")
        print("\n========= Client Logs =========\n")
        client = StatusClient()
        client.submit_job()
        end_status = client.wait_complete(StatusClient.WaitArgs())
        print(f"Wait finished with status: {end_status}")
        print(client.stats)


if __name__ == "__main__":
    unittest.main()
