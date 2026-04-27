from DIPPID import SensorUDP

PORT = 5700
sensor = SensorUDP(PORT)

def handle_accelerometer(data):
    print(data)

def handle_button_1(data):
    print(data)

sensor.register_callback('accelerometer', handle_accelerometer)
sensor.register_callback('button_1', handle_button_1)