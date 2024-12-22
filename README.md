# Server-Query
A simple client request library. Given a basic server with endpoint that returns the status only with minimal additional functionality, this client library provides methods to query the status.

## Getting Started
To run an example manually, start up the server 
```
python server/server.py
```
Then run main in the client library script in a separate terminal
```
python server/client.py
```


## Library Usage
A simple example usage will look something like this
```python
# Create client object
client = StatusClient()

# Submit job request to server
client.submit_job()

# Block until job complete (or errors out)
args = StatusClient.WaitArgs()
end_status = client.wait_complete()

# ----- post completion logic (i.e. retrieve video data) -----
```
The user must create a client and then submit a job. The library provides the user with a method `wait_complete()` for waiting until a submitted job has completed. The waiting policy can be customized with `WaitArgs` to either use a backoff strategy to minimize request count or use a constant check strategy to minimize the lag between server completion and `wait_complete()` unblocking. One may be more appropriate than the other depending on use case. 

The user may also choose to use `client.get_status()` to get the immediate status of the job should they wish to implement their own waiting, though this is not recommended. 

## Testing
Install `requirements.txt` dependencies. Run integration tests with the following
```
python -m unittest tests/test_integration.py
```
Example output:
```
usr@computer % python -m unittest tests/test_integration.py

[TEST]: Server started
[TEST]: Client running

========= Client Logs =========

[StatusClient]  Job started successfully
[StatusClient]  Checked status and got response: {'result': 'pending'}. Retrying
[StatusClient]  Checked status and got response: {'result': 'pending'}. Retrying
[StatusClient]  Checked status and got response: {'result': 'pending'}. Retrying
[StatusClient]  Checked status and got response: {'result': 'pending'}. Retrying
[StatusClient]  Job completed. Lag: 3.66 seconds, Total Jobs: 1, Total Requests: 5
Wait finished with status: Status.COMPLETED
Client Performance Statistics:
  Total Jobs Submitted : 1
  Total Requests Made  : 5
  Total Lag (seconds)  : 3.6570115089
.
========= Server Logs (stdout) =========
  * Serving Flask app 'server'
 * Debug mode: on


========= Server Logs (stderr) =========
 WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 145-047-763
127.0.0.1 - - [21/Dec/2024 20:35:01] "POST /start HTTP/1.1" 202 -
127.0.0.1 - - [21/Dec/2024 20:35:01] "GET /status HTTP/1.1" 202 -
127.0.0.1 - - [21/Dec/2024 20:35:02] "GET /status HTTP/1.1" 202 -
127.0.0.1 - - [21/Dec/2024 20:35:04] "GET /status HTTP/1.1" 202 -
127.0.0.1 - - [21/Dec/2024 20:35:08] "GET /status HTTP/1.1" 202 -
127.0.0.1 - - [21/Dec/2024 20:35:16] "GET /status HTTP/1.1" 200 -


----------------------------------------------------------------------
Ran 1 test in 16.077s

OK
```