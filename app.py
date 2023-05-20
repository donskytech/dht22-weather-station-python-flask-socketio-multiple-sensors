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

thread_1 = None
thread_lock_1 = Lock()

thread_2 = None
thread_lock_2 = Lock()

thread_3 = None
thread_lock_3 = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "donsky!"
socketio = SocketIO(app, cors_allowed_origins="*")

"""
Background Thread
"""


def background_thread_1():
    while True:
        # DHT 1
        temperature, humidity = dht22_module_1.get_sensor_readings()
        sensor_readings = {
            "id": dht22_module_1.get_id(),
            "temperature": temperature,
            "humidity": humidity,
        }
        socketio.emit("updateSensorData", json.dumps(sensor_readings))


def background_thread_2():
    while True:
        # DHT2
        temperature, humidity = dht22_module_2.get_sensor_readings()
        sensor_readings = {
            "id": dht22_module_2.get_id(),
            "temperature": temperature,
            "humidity": humidity,
        }
        socketio.emit("updateSensorData", json.dumps(sensor_readings))


def background_thread_3():
    while True:
        # DHT2
        temperature, humidity = dht22_module_3.get_sensor_readings()
        sensor_readings = {
            "id": dht22_module_3.get_id(),
            "temperature": temperature,
            "humidity": humidity,
        }
        socketio.emit("updateSensorData", json.dumps(sensor_readings))


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
    global thread_1
    global thread_2
    global thread_3
    print("Client connected")

    with thread_lock_1:
        if thread_1 is None:
            thread_1 = socketio.start_background_task(background_thread_1)

    with thread_lock_2:
        if thread_2 is None:
            thread_2 = socketio.start_background_task(background_thread_2)

    with thread_lock_3:
        if thread_3 is None:
            thread_3 = socketio.start_background_task(background_thread_3)


"""
Decorator for disconnect
"""


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


if __name__ == "__main__":
    socketio.run(app, port=5000, host="0.0.0.0", debug=True)
