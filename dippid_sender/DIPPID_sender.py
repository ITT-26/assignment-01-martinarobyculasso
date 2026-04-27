import socket
import json
import time
import random
import math

IP = '127.0.0.1'    # localhost
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# simulated initial button state
button_1 = "released"

# frequencies for the simulated accelerometer data
freq_x = 1.0            
freq_y = 0.3
freq_z = 1.7

# phase shifts for the simulated accelerometer data
phase_shift_x = 1.0
phase_shift_y = 0.0 
phase_shift_z = 2.3

while True:
    randin = random.randint(0, 100)
    if randin < 20:
        toggle = True
    else:        
        toggle = False

    if toggle:
        if button_1 == "released":
            button_1 = "pressed"
        else:
            button_1 = "released"

    message_dict = {
        "accelerometer":{
            "x": str(math.sin(freq_x * time.time() + phase_shift_x)),
            "y": str(math.sin(freq_y * time.time() + phase_shift_y)),
            "z": str(math.sin(freq_z * time.time() + phase_shift_z))
        },

        "button_1": button_1,
    }

    message = json.dumps(message_dict)

    print(message)

    sock.sendto(message.encode(), (IP, PORT))

    time.sleep(1)     # data is sent every 1 second