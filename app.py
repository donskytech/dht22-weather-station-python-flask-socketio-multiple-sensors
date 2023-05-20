import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
from dht22_module import DHT22Module

# import board

# dht22_module = DHT22Module(board.D18)
dht22_module_1 = DHT22Module(1)
dht22_module_2 = DHT22Module(2)
dht22_module_3 = DHT22Module(3)

thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "donsky!"
socketio = SocketIO(app, cors_allowed_origins="*")

"""
Background Thread
"""


def background_thread():
    while True:
        # DHT 1
        temperature, humidity = dht22_module_1.get_sensor_readings()
        sensor_readings = {
            "id": dht22_module_1.get_id(),
            "temperature": temperature,
            "humidity": humidity,
        }
        socketio.emit("updateSensorData", json.dumps(sensor_readings))
        socketio.sleep(1)
        # DHT2
        temperature, humidity = dht22_module_2.get_sensor_readings()
        sensor_readings = {
            "id": dht22_module_2.get_id(),
            "temperature": temperature,
            "humidity": humidity,
        }
        socketio.emit("updateSensorData", json.dumps(sensor_readings))
        socketio.sleep(1)
        # DHT3
        temperature, humidity = dht22_module_3.get_sensor_readings()
        sensor_readings = {
            "id": dht22_module_3.get_id(),
            "temperature": temperature,
            "humidity": humidity,
        }
        socketio.emit("updateSensorData", json.dumps(sensor_readings))
        socketio.sleep(1)


"""
Serve root index file
"""


@app.route("/")
def index():
    return render_template("index.html")


"""
Decorator for connect
"""


@socketio.on("connect")
def connect():
    global thread
    global thread_2
    global thread_3
    print("Client connected")

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


"""
Decorator for disconnect
"""


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


if __name__ == "__main__":
    socketio.run(app, port=5000, host="0.0.0.0", debug=True)
