from flask import Flask, jsonify
import random
import json
import time
import threading

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

# Job configuration parameters
TIME_MINIMUM = app.config.get("TIME_MINIMUM", 0)
TIME_RANGE = app.config.get("TIME_RANGE", 0)

# Error configuration parameters
ERROR_FREQ = app.config.get("ERROR_FREQUENCY", 0)
ERROR_PROBABILITY = app.config.get("ERROR_PROBABILITY", 0)
random.seed(app.config.get("RANDOM_SEED", 0))

# Job state
has_errored = False
start_time = -1


def job_task():
    global has_errored
    global start_time
    start_time = time.time()
    while True:
        time.sleep(ERROR_FREQ)
        if random.random() < ERROR_PROBABILITY:
            has_errored = True


# Start the job
@app.route("/start", methods=["POST"])
def start_job():
    threading.Thread(target=job_task, daemon=True).start()
    return jsonify({"result": "success"})


# GET endpoint to return status
@app.route("/status", methods=["GET"])
def get_status():
    if start_time == -1:
        return jsonify({"result": "error"})  # error if not started
    elif has_errored:
        return jsonify({"result": "error"})
    elif time.time() - start_time < TIME_MINIMUM:
        return jsonify({"result": "pending"})
    elif time.time() - start_time >= TIME_MINIMUM + TIME_RANGE:
        return jsonify({"result": "completed"})
    return jsonify({"result": "error"})


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"])
