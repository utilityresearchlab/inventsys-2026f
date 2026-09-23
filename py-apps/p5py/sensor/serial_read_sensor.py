# Reads serial data from an arduino that passes a single value from 0 to 1023
# @author: mriveralee / UtilityResearchLab.org
# Uses the arduino/Arduino-SerialSendValue.ino sketch
# Requires pyserial

from p5 import *

import serial
import time

# Serial Setup
SERIAL_PORT_NAME = '/dev/cu.usbserial-130'
SERIAL_PORT = None
SERIAL_BAUD = 9600
SERIAL_TIMEOUT = 0.01
SERIAL_PORT = serial.Serial(SERIAL_PORT_NAME, baudrate=SERIAL_BAUD, timeout=SERIAL_TIMEOUT)


SENSOR_VALUE_MIN = 0
SENSOR_VALUE_MAX = 1023

# Params
y = 0
latest_value = 0
serial_buffer = ""

# The statement in setup() function
# execute once when the program begins
def setup():
    size(640, 360) # size must be the first statement
    stroke(255) # Set line drawing color to white
    y = 0
    print("Serial port: %s" % SERIAL_PORT.port if SERIAL_PORT else "None")
    print("Finished the setup.")
    

# The statements in draw() are executed until the
# program is stopped. Each statement is executed in
# sequence and after the last line is read, the first
# line is executed again.
def draw():
    global y
    global latest_value, serial_buffer
    
    # Read all currently available bytes without waiting
    if (SERIAL_PORT):
        while SERIAL_PORT.in_waiting > 0:
           byte_data = SERIAL_PORT.read(1)
           serial_buffer += byte_data.decode("utf-8", errors="ignore")

        # Process every complete line currently in the buffer
        while "\n" in serial_buffer:
            latest_serial_data = ""
            latest_serial_data, serial_buffer = serial_buffer.split("\n", 1)
            latest_serial_data = latest_serial_data.strip()

            if latest_serial_data:
               serial_event(latest_serial_data)

    
    background(0) # Clear the screen with a black background

    # Draw sensor value as text at (X, Y) position
    fill(255)
    text_size(20)
    text(str(latest_value), (width / 2, height / 2)) # width and height are global p5 vars
    
    # Draw line across screen
    y = y - 1
    if y < 0:
        y = height
    line((0, y), (width, y))
    
    

# Process the serial data received from draw
def serial_event(data):
    global latest_value

    latest_value = data
    print("Received:", data, flush=True)


def key_pressed():
    if key == "ENTER":
        exitApp()

def exitApp():
    if SERIAL_PORT is not None and SERIAL_PORT.is_open:
        SERIAL_PORT.close()
        print("Serial port closed")
    print("Exiting")
    exit()
        
        

# Run the P5 Application
if __name__ == '__main__':
    # p5 supports different backends to render sketches,
    # "vispy" for both 2D and 3D sketches & "skia" for 2D sketches
    # use "skia" for better 2D experience
    # Default renderer is set to "vispy"
    print("Starting application...")
    #run(renderer="vispy") # vispy crashes for text size changes
    run(renderer="skia") # "skia" is still in beta, skia works with text_size


