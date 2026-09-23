# A processing sketch that captures audio and displays the waveform
# with the FFT spectrum. 
# @author: mriveralee / UtilityResearchLab.org
# Three different FFT types can be displays a basic FFT, a normalized FFT, and an FFT with Hanning Window
# # The sketch also includes the ability to toggle low pass and high pass filters (which are set below)
# Keyboard Input:
# 'l' : toggle low pass filter
# 'h' : toggle high pass filter
# 't' : cycle through FFT types
# 'q' : close audio input and quit app
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
BLOCK_SIZE = 1024 # this is used both for audio input and FFT processing

LOW_PASS_FILTER_FREQ = 3000 # a low pass freq, if enabled
HIGH_PASS_FILTER_FREQ = 2000 # a high pass freq, if enabled


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
    current_fft_type = 1 # 0 = Basic FFT; 1 = Normalized; 2 = Hanning
    use_low_pass_filter = False
    use_high_pass_filter = False

    def __init__(self):
        # Attach our callback to the audio stream
        print("Init App State")
        print("Setting up audio input")
        self.audio_input.init_audio_stream(audio_stream_callback)
        self.audio_input.start_audio_stream()

# Declare AppState Object globally
APP_STATE = AppState()


# Helper function to apply a low pass filter to fft values
def apply_low_pass_filter(low_pass_fq, num_samples, sample_rate, fft_values):
    # Frequency represented by each FFT bin
    frequencies = np.fft.rfftfreq(num_samples, d=1 / sample_rate)

    # Remove frequencies above the cutoff
    fft_values[frequencies > low_pass_fq] = 0

    return fft_values

# Helper function to apply a low pass filter to fft values
def apply_high_pass_filter(high_pass_fq, num_samples, sample_rate, fft_values):
    # Frequency represented by each FFT bin
    frequencies = np.fft.rfftfreq(num_samples, d=1 / sample_rate)

    # Remove frequencies below the cutoff
    fft_values[frequencies < high_pass_fq] = 0

    return fft_values

# FFT Helper Functions
# A basic FFT spectrum
def calculate_fft_spectrum(samples):
    # Real-valued FFT
    fft_values = np.fft.rfft(samples)

    # Optionally apply low pass filter
    if APP_STATE.use_low_pass_filter:
            fft_values = apply_low_pass_filter(LOW_PASS_FILTER_FREQ, len(samples), SAMPLE_RATE, fft_values)

    # Optionally apply high pass filter
    if APP_STATE.use_high_pass_filter:
            fft_values = apply_high_pass_filter(HIGH_PASS_FILTER_FREQ, len(samples), SAMPLE_RATE, fft_values)

    # Magnitude spectrum
    magnitude = np.abs(fft_values)

    # Convert to decibels
    magnitude_db = 20 * np.log10(magnitude + 1e-8)

    # Clamp and normalize for display
    magnitude_db = np.clip(magnitude_db, -80, 0)
    normalized = (magnitude_db + 80) / 80

    return normalized

# A basic FFT spectrum that has normalized magnitudes
def calculate_fft_spectrum_normalized(samples):
    fft_values = np.fft.rfft(samples)

    # Optionally apply low pass filter
    if APP_STATE.use_low_pass_filter:
        fft_values = apply_low_pass_filter(LOW_PASS_FILTER_FREQ, len(samples), SAMPLE_RATE, fft_values)

    # Optionally apply high pass filter
    if APP_STATE.use_high_pass_filter:
        fft_values = apply_high_pass_filter(HIGH_PASS_FILTER_FREQ, len(samples), SAMPLE_RATE, fft_values)

    magnitude = np.abs(fft_values) / len(samples)

    # Account for discarded negative-frequency bins
    if len(magnitude) > 2:
        magnitude[1:-1] *= 2

    magnitude_db = 20 * np.log10(magnitude + 1e-8)

    magnitude_db = np.clip(magnitude_db, -80, 0)
    return (magnitude_db + 80) / 80

# A FFT spectrum using a Hanning Window
# A Hann window reduces sharp discontinuities at the block edges.
# In addition converting the magnitude to decibels makes quiet frequencies easier to see
def calculate_fft_spectrum_hanning(samples):
    # Reduce spectral leakage
    windowed = samples * np.hanning(len(samples))

    # Real-valued FFT: only non-negative frequencies are needed
    fft_values = np.fft.rfft(windowed)

    # Optionally apply low pass filter
    if APP_STATE.use_low_pass_filter:
        fft_values = apply_low_pass_filter(LOW_PASS_FILTER_FREQ, len(samples), SAMPLE_RATE, fft_values)

    # Optionally apply high pass filter
    if APP_STATE.use_high_pass_filter:
        fft_values = apply_high_pass_filter(HIGH_PASS_FILTER_FREQ, len(samples), SAMPLE_RATE, fft_values)

    # Magnitude spectrum
    magnitude = np.abs(fft_values)

    # Convert to decibels
    magnitude_db = 20 * np.log10(magnitude + 1e-8)

    # Normalize for display
    magnitude_db = np.clip(magnitude_db, -80, 0)
    normalized = (magnitude_db + 80) / 80

    return normalized

# The statement in setup() function
# execute once when the program begins
def setup():
    # use global to access global primitives
    # note this is not the best practice
    size(1000, 600) # size must be the first statement
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

     # -------------------------
    # Waveform: upper half
    # -------------------------
    stroke(70)
    line(0, height * 0.25, width, height * 0.25)

    stroke(0, 220, 120)
    stroke_weight(2)
    no_fill()

    begin_shape()

    for i, sample in enumerate(samples):
        x = remap(i, (0, len(samples) - 1), (0, width))
        y = height * 0.25 - sample * height * 0.20
        vertex(x, y)

    end_shape()

    # -------------------------
    # FFT spectrum: lower half
    # -------------------------
    spectrum = None
    match APP_STATE.current_fft_type:
        case 0:
            spectrum = calculate_fft_spectrum(samples)
        case 1:
            spectrum = calculate_fft_spectrum_normalized(samples)
        case 2:                 
            spectrum = calculate_fft_spectrum_hanning(samples)
        case _:
            print("Unknown FFT type - using basic fft")
            spectrum = calculate_fft_spectrum(samples)

    spectrum_top = height * 0.52
    spectrum_bottom = height * 0.95
    spectrum_height = spectrum_bottom - spectrum_top

    stroke(70)
    line(0, spectrum_top, width, spectrum_top)

    stroke(80, 150, 255)
    stroke_weight(2)
    no_fill()

    # The first half of the spectrum is usually enough.
    bins_to_draw = len(spectrum) // 2
    visible_spectrum = spectrum[1:bins_to_draw]
    bar_width = width / len(visible_spectrum)

    # Draw rectangles from the bottom upward
    no_stroke()
    fill(50, 130, 255, 180)
    for i, magnitude in enumerate(visible_spectrum):
        x = i * bar_width
        bar_height = magnitude * spectrum_height
        y = spectrum_bottom - bar_height
        rect(
            x,
            y,
            max(1, bar_width - 1),
            bar_height,
        )

    # Optional outline showing the FFT curve over the bars
    stroke(120, 200, 255)
    stroke_weight(2)
    no_fill()

    begin_shape()

    for i, magnitude in enumerate(visible_spectrum):
        x = i * bar_width + bar_width / 2
        y = spectrum_bottom - magnitude * spectrum_height
        vertex(x, y)

    end_shape()

# Handle key input
def key_pressed(event):
    if key == "q":
        APP_STATE.audio_input.audio_stream.stop()
        APP_STATE.audio_input.audio_stream.close()
        print("Exiting.")
        exit()
    if key == 't':
        # Increment fft type and cap at the max number of types
        APP_STATE.current_fft_type = (APP_STATE.current_fft_type + 1) % 3
        fft_type_name = "None"
        match APP_STATE.current_fft_type:
            case 0:
                fft_type_name = "Basic FFT"
            case 1:
                fft_type_name = "Normalized FFT"
            case 2:                 
                fft_type_name = "Hanning FFT"
            case _:
                fft_type_name = "Unknown FFT Type"
        print("Current FFT Type: %s " % fft_type_name)
    if key == 'l':
        AppState.use_low_pass_filter = not AppState.use_low_pass_filter
        print("Low Pass Filter (%s): %s" % (LOW_PASS_FILTER_FREQ, ("ON" if  AppState.use_low_pass_filter else "OFF")))
    if key == 'h':
           AppState.use_high_pass_filter = not AppState.use_high_pass_filter
           print("High Pass Filter (%s): %s" % (HIGH_PASS_FILTER_FREQ, ("ON" if  AppState.use_high_pass_filter else "OFF")))
      
    
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


