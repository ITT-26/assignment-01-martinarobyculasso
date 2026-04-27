import socket
import json
import time
import random
import math

IP = '127.0.0.1'    # localhost
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# simulated initial button state
button_1 = 0        # 0 -> released , 1 -> pressed

# amplitudes for the simulated accelerometer data
a_x = 0.8
a_y = 0.6
a_z = 1.0

# frequencies for the simulated accelerometer data
freq_x = 3.0            
freq_y = 2.5
freq_z = 1.9

# phase shifts for the simulated accelerometer data
phase_shift_x = 1.0
phase_shift_y = 0.0 
phase_shift_z = 2.3

while True:
    randin = random.randint(0, 100)
    if randin < 5:
        toggle = True   # 5% chance of changing the button state every iteration
    else:        
        toggle = False

    if toggle:
        if button_1 == 0:
            button_1 = 1
        else:
            button_1 = 0

    message_dict = {
        "accelerometer":{
            "x": str(a_x*math.sin(freq_x * time.time() + phase_shift_x)),
            "y": str(a_y*math.sin(freq_y * time.time() + phase_shift_y)),
            "z": str(a_z*math.sin(freq_z * time.time() + phase_shift_z) + 1.0)      # z-axis centered around 1g
        },

        "button_1": str(button_1),
    }

    message = json.dumps(message_dict)

    print(message)

    sock.sendto(message.encode(), (IP, PORT))

    time.sleep(0.1)     # data is sent every 0.1 seconds - actual sensor data could be sent at a different rate (usually higher)