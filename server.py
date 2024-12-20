from flask import Flask, jsonify
import random

app = Flask(__name__)


# GET endpoint to return status
@app.route("/status", methods=["GET"])
def get_status():
    # Randomly choose a status for demonstration
    statuses = ["pending", "completed", "error"]
    status = random.choice(statuses)

    return jsonify({"result": status})


if __name__ == "__main__":
    app.run(debug=True)
