# A processing sketch that captures audio and displays the waveform
# @author: mriveralee / UtilityResearchLab.org
# 1) Requires p5, numpy, sounddevice: `pip install p5 sounddevice numpy`
# If you installed the requirements.txt, you should be good to go.
# 2) Note: If you run into issues using the microphone, 
# you may need to grant microphone permission to the Python and/or Terminal process.
# 3) If you have multiple input devices, you will need to query devices using sounddevice,
# and choose the correct device ID. Then add the "device=DEVICE_NUMBER" param to the sd.InputStream
# setup in the UserAudioInput class
# ```
#   import sounddevice as sd
#   print(sd.query_devices())
# ```
from p5 import *

import threading

import numpy as np
import sounddevice as sd

# Audio configuration
DEVICE_NUMBER = 1 # change to correct input based on the sd.query_devices() printed in the console
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024

# Helper Class to hold our audio input
class UserAudioInput:
    # Shared waveform buffer
    waveform = np.zeros(BLOCK_SIZE, dtype=np.float32)
    waveform_lock = threading.Lock()
    audio_stream = None
    is_started = False

    # Creates the microphone input stream
    def init_audio_stream(self, audio_received_callback):
        print("Init audio input stream...")
        # Start microphone capture
        self.audio_stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            device=DEVICE_NUMBER,
            channels=1,
            dtype="float32",
            callback=audio_received_callback,
        )

    def start_audio_stream(self):
        if self.is_started:
            print("Audio stream already started!")
            return
        print("Starting audio input stream...")
        self.is_started = True
        self.audio_stream.start()
        


    # This is a secondary callback that receives audio data
    def process_audio_input(self, indata, frame, time, status):
        if status:
            print(status)
        # Use the first channel if the microphone is stereo
        samples = indata[:, 0]

        with self.waveform_lock:
            n = min(len(samples), len(self.waveform))
            self.waveform[:n] = samples[:n]

            if n < len(self.waveform):
                self.waveform[n:] = 0

# Our callback is separate from the UserAudioInput
def audio_stream_callback(indata, frames, time, status):
    # Forward callback to the app state
    APP_STATE.audio_input.process_audio_input(indata, frames, time, status)


# Use app state for parameters
class AppState:
    # This is our audio input stored in the app state
    audio_input = UserAudioInput()

    def __init__(self):
        # Attach our callback to the audio stream
        print("Init App State")
        print("Setting up audio input")
        self.audio_input.init_audio_stream(audio_stream_callback)
        self.audio_input.start_audio_stream()

# Declare AppState Object globally
APP_STATE = AppState()

# The statement in setup() function
# execute once when the program begins
def setup():
    # use global to access global primitives
    # note this is not the best practice
    size(640, 360) # size must be the first statement
    stroke(255) # Set line drawing color to white
    stroke_weight(2) # set line weight
    print("Finished the setup.")
    

# The statements in draw() are executed until the
# program is stopped. Each statement is executed in
# sequence and after the last line is read, the first
# line is executed again.
def draw():
    background(0) # Clear the screen with a background

    # Center line
    stroke(80)
    #line(0, height / 2, width, height / 2)

    # Grab waveform lock
    with APP_STATE.audio_input.waveform_lock:
        samples = APP_STATE.audio_input.waveform.copy()

    stroke(0, 220, 120)
    no_fill()

    # Draw waveform on canvas
    begin_shape()
    for i, sample in enumerate(samples):
        # Note map in processing java / p5js != map in p5py. 
        # The equivalent function in p5py is `remap` with the ranges as tuples
        x = remap(i, (0, len(samples) - 1), (0, width))

        # Microphone samples usually fall roughly between -1 and 1
        y = height / 2 - sample * height * 0.45

        vertex(x, y)
    end_shape()

# Handle key input
def key_pressed(event):
    if key == "q":
        APP_STATE.audio_input.audio_stream.stop()
        APP_STATE.audio_input.audio_stream.close()
        print("Exiting.")
        exit()
   
    
# Run the P5 Application
if __name__ == '__main__':
    # Print Audio Devices:
    print(sd.query_devices())
    print("Current Device Numbers = ", DEVICE_NUMBER)
    # p5 supports different backends to render sketches,
    # "vispy" for both 2D and 3D sketches & "skia" for 2D sketches
    # use "skia" for better 2D experience
    # Default renderer is set to "vispy"
    print("Starting application...")
    run(renderer="vispy") # vispy crashes for text size changes;
    #run(renderer="skia") # "skia" is still in beta, skia works with text_size


