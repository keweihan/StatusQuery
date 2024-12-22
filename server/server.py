from flask import Flask, jsonify
import random
import json
import time
import threading
import typing

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

# Job configuration parameters
JOB_DURATION = app.config.get("JOB_DURATION", 0)
JOB_VARIANCE = app.config.get("JOB_VARIANCE", 0)

# Error configuration parameters
ERROR_FREQ = app.config.get("ERROR_FREQUENCY", 0)
ERROR_PROBABILITY = app.config.get("ERROR_PROBABILITY", 0)


# Job state
has_errored = False
is_finished = False
start_time = -1
error_thread: threading.Thread = None
job_duration_real = -1


def job_task():
    """Simulate job that may error"""
    global has_errored
    global start_time
    global job_duration_real

    has_errored = False
    is_finished = False
    start_time = time.time()
    job_duration_real = JOB_DURATION + random.uniform(-1, 1) * JOB_VARIANCE

    while not is_finished:
        time.sleep(ERROR_FREQ)
        if random.random() < ERROR_PROBABILITY:
            has_errored = True


@app.route("/start", methods=["POST"])
def start_job():
    """Start the job"""
    global error_thread
    error_thread = threading.Thread(target=job_task, daemon=True).start()
    return jsonify({"result": "success"}), 202


@app.route("/status", methods=["GET"])
def get_status():
    """Return status of job"""
    print(f"job_duration: {job_duration_real}")
    print(f"time since start job: {time.time() - start_time}")
    if start_time == -1:
        print("Job not started")
        return jsonify({"result": "error"}), 404
    elif has_errored:
        print("Job errored")
        return jsonify({"result": "error"}), 500
    elif time.time() - start_time < job_duration_real:
        return jsonify({"result": "pending"}), 202
    elif time.time() - start_time >= job_duration_real:
        global is_finished
        is_finished = True

        # Add real job completion time to response (for profiling/testing purposes)
        return jsonify({"result": "completed", "_completion_time": start_time + job_duration_real}), 200
    return jsonify({"result": "error"}), 500


if __name__ == "__main__":
    if app.config.get("USE_SEED", True):
        random.seed(app.config.get("RANDOM_SEED", 0))
    app.run(host="127.0.0.1", debug=app.config["DEBUG"], port=app.config["PORT"])
