# Reads serial data for a joystick's sensor values for SW, X, and Y
# @author: mriveralee / UtilityResearchLab.org
# The values are ordered <SW>,<X>,<Y> and range from 0 to 1023
# Note that the switch is binary, either 0 or 1023.
# Uses the arduino/Arduino_SerialSendJoystick.ino sketch
# Requires pyserial

from p5 import *

import serial
import time

# Serial Setup
SERIAL_PORT_NAME = '/dev/cu.usbserial-130'
SERIAL_BAUD = 9600
SERIAL_TIMEOUT = 0.01
SERIAL_PORT = serial.Serial(SERIAL_PORT_NAME, baudrate=SERIAL_BAUD, timeout=SERIAL_TIMEOUT)

# Sensor Data Constants
SENSOR_DATA_DELIMITER = "," # separates each sensor value
SENSOR_VALUE_MIN = 0
SENSOR_VALUE_MAX = 1023

# Use app state for parameters
class AppState:
    x = 0
    y = 0
    sw = False
    latest_value = 0
    serial_buffer = ""

# Declare  AppState Object globally
APP_STATE = AppState()


# The statement in setup() function
# execute once when the program begins
def setup():
    size(640, 360) # size must be the first statement
    stroke(255) # Set line drawing color to white
    print("Sketch Name:", "Serial Read Joystick")
    APP_STATE.y = 0
    if (not SERIAL_PORT):
        print("Error: Serial port not defined!")
    print("Finished the setup.")


    

# The statements in draw() are executed until the
# program is stopped. Each statement is executed in
# sequence and after the last line is read, the first
# line is executed again.
def draw():
    # Read all currently available bytes without waiting
    # this is non-block to avoid delaying drawing updates
    if (SERIAL_PORT):
        while SERIAL_PORT.in_waiting > 0:
           byte_data = SERIAL_PORT.read(1)
           APP_STATE.serial_buffer += byte_data.decode("utf-8", errors="ignore")

        # Process every complete line currently in the buffer
        while "\n" in APP_STATE.serial_buffer:
            APP_STATE.latest_serial_data = ""
            APP_STATE.latest_serial_data, APP_STATE.serial_buffer = APP_STATE.serial_buffer.split("\n", 1)
            APP_STATE.latest_serial_data = APP_STATE.latest_serial_data.strip()

            if APP_STATE.latest_serial_data:
               serial_event(APP_STATE.latest_serial_data)
    
    background(0) # Clear the screen with a black background

    # Draw sensor value at (X, Y) position
    fill(255)
    text_size(20)
    text(str(APP_STATE.latest_value), (320, 200))
    
    if (APP_STATE.sw):
        stroke(255, 0, 30)
    else:
        stroke(255)
    line((0, APP_STATE.y), (width, APP_STATE.y))
    line((APP_STATE.x, 0), (APP_STATE.x, height))

# Process the serial data received
# based on a newline as delimiter
def serial_event(data):
    APP_STATE.latest_value = data
    # Data is of format <sw>,<x>,<y>
    # split on the comma, cast to int
    vals = data.split(SENSOR_DATA_DELIMITER)
    if (len(vals) < 3):
        print("Incomplete serial data. Skipping:", APP_STATE.latest_value)
        return
    APP_STATE.x = remap(int(vals[1]), (SENSOR_VALUE_MIN, SENSOR_VALUE_MAX), (0, width))
    APP_STATE.y = remap(int(vals[2]), (SENSOR_VALUE_MIN, SENSOR_VALUE_MAX), (0, height))
    APP_STATE.sw = bool(remap(int(vals[0]), (SENSOR_VALUE_MIN, SENSOR_VALUE_MAX), (0, 1)))
    print("Received: %s" % data, flush=True)


# Handles Key press events
def key_pressed():
    if key == "ENTER":
        exitApp()

# Exits the app after cleaning up
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
    

