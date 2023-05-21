import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from threading import Lock
from dht22_module import DHT22Module
import board
import adafruit_dht

dht22_module_1 = DHT22Module(1, board.D2)
dht22_module_2 = DHT22Module(2, board.D3, adafruit_dht.DHT11)
dht22_module_3 = DHT22Module(3, board.D4)

dht_modules = [dht22_module_1, dht22_module_2, dht22_module_3]

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
        for dht in dht_modules:
            # Scan through all DHT sensor connected to our raspberry pi
            temperature, humidity = dht.get_sensor_readings() or (None, None)
            if temperature is not None or humidity is not None:
                sensor_readings = {
                    "id": dht.get_id(),
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
    return render_template("index.html", dht_modules=dht_modules)


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
