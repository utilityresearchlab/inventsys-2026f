'''
Repeatedly generates an ultrasonic frequency sweep (inaudible) from 
LOW_FREQUENCY to HIGH_FREQUENCY across SWEEP_DURATION and plays it
through the speakers. At the same time, records audio input using 
the microphone. The microphone input is processed using and FFT and
the results are displayed on a realtime spectrogram.

NOTE: Make sure you chose the correct INPUT_DEVICE and OUTPUT_DEVICE,
 the console / terminal window will show the inputs you have available to you with indicies
 
As you interact with the speakers, you'll see the sweep frequenies become
attenuated. If you couple this with machine learning you can use it to 
detect gestures or other inputs. 

You can also use the spectrogram to explore different times of audible sounds. 
For example, notice the different between a nail tap and a knuckle tap on your
laptop, or the table. Compare a clap vs. a whistle.
'''

import queue
import time

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import chirp, get_window

# -----------------------------
# Audio configuration
# -----------------------------
SAMPLE_RATE = 96_000 #44_100 # MBpro should have 96kHz max sample rate so it can capture Ultrasound

SWEEP_DURATION = 1.0 # usually you want this to be relatively small

LOW_FREQUENCY = 18000.0
HIGH_FREQUENCY = 22050.0
OUTPUT_AMPLITUDE = 0.05 # keep this low to avoid blowing your speakers out!

BLOCK_SIZE = 1024 
CHANNELS = 1

# Display settings
# the number of fft bins, so SAMPLE_RATE / 4096 will give the range of frequencies captured in a bin
FFT_SIZE = 4096  
DISPLAY_SECONDS = 10
DISPLAY_MIN_FREQUENCY = 0
DISPLAY_MAX_FREQUENCY = 22050 # at most can be SAMPLE_RATE / 2 (the nyquist frequency)

# CHANGE THESE TO MATCH YOUR SYSTEM
# Set to the below to None to use the system defaults.
# Input is microphone
INPUT_DEVICE = 2 #3 for mbp mic  
# Output is speaker 
OUTPUT_DEVICE = 3 #4 for mbp mic


# -----------------------------
# Generate repeating sweep
# -----------------------------
def make_sweep():
    sample_count = int(SWEEP_DURATION * SAMPLE_RATE)
    t = np.arange(sample_count) / SAMPLE_RATE
    
    # Chirp is the equivalent of a sweep function in scipy 
    sweep = chirp(
        t,
        f0=LOW_FREQUENCY,
        f1=HIGH_FREQUENCY,
        t1=SWEEP_DURATION,
        method="logarithmic",
    )

    # Fade the sweep boundaries to prevent clicks
    fade_samples = int(0.02 * SAMPLE_RATE)
    fade = np.sin(np.linspace(0, np.pi / 2, fade_samples)) ** 2

    envelope = np.ones(sample_count)
    envelope[:fade_samples] = fade
    envelope[-fade_samples:] = fade[::-1]

    return (OUTPUT_AMPLITUDE * sweep * envelope).astype(np.float32)


sweep = make_sweep()
sweep_position = 0

# The callback writes microphone data here.
audio_queue = queue.Queue(maxsize=50)


# -----------------------------
# Audio callback
# -----------------------------
def audio_callback(indata, outdata, frames, time_info, status):
    global sweep_position

    if status:
        print(status)

    # Put a copy of microphone input into the queue.
    try:
        audio_queue.put_nowait(indata[:, 0].copy())
    except queue.Full:
        # Drop the oldest block if plotting falls behind.
        try:
            audio_queue.get_nowait()
            audio_queue.put_nowait(indata[:, 0].copy())
        except queue.Empty:
            pass

    # Generate repeating sweep output.
    output = np.empty(frames, dtype=np.float32)

    first_count = min(frames, len(sweep) - sweep_position)
    output[:first_count] = sweep[
        sweep_position:sweep_position + first_count
    ]

    remaining = frames - first_count

    if remaining:
        output[first_count:] = sweep[:remaining]
        sweep_position = remaining
    else:
        sweep_position += first_count
        if sweep_position >= len(sweep):
            sweep_position = 0

    outdata[:, 0] = output


# -----------------------------
# Spectrogram state
# -----------------------------
frequency_bins = np.fft.rfftfreq(FFT_SIZE, 1 / SAMPLE_RATE)

# The minimum FFT bin we will care about for the Spectrogram display
min_bin = np.searchsorted(
    frequency_bins,
    DISPLAY_MIN_FREQUENCY,
)

# The maximum FFT bin we will care about for the Spectrogram display
max_bin = np.searchsorted(
    frequency_bins,
    DISPLAY_MAX_FREQUENCY,
)

frequency_bins = frequency_bins[min_bin:max_bin]

# Number of FFT columns shown.
column_count = max(
    1,
    int(DISPLAY_SECONDS * SAMPLE_RATE / BLOCK_SIZE),
)

# Will store the data for display in the plot
spectrogram_data = np.full(
    (len(frequency_bins), column_count),
    -100.0,
    dtype=np.float32,
)

# FFT windowing using Hann fxn which smooths the signal
window = get_window("hann", FFT_SIZE)


# Computes an FFT over a block and returns the decibel result for the range
# from min_bin to max_bin (as defined above). 
# Note that this is different that the LOW / HIGH frequency for our ultrasound
# as we want to display as much of the FFT bins in the spectrogram and the LOW/HIGH
# is only for sweeping.
def compute_fft(block):
    """Return the positive-frequency magnitude spectrum in dB."""
    if len(block) < FFT_SIZE:
        padded = np.zeros(FFT_SIZE, dtype=np.float32)
        padded[-len(block):] = block
        block = padded
    else:
        block = block[-FFT_SIZE:]
    
    # Normalizes the input to remove DC Offset
    block = block - np.mean(block)
    
    # Returns only the positive FFT values
    # the input is the windowing function (hann as specified above) f
    # unction applied to the bloc
    spectrum = np.fft.rfft(block * window)

    # Normalize magnitude and convert to dB.
    magnitude = np.abs(spectrum) / np.sum(window)
    magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-10))
    
    return magnitude_db[min_bin:max_bin]


# Updates the plot with the latest spectrogram data
# This is called from out animation function down below
def update_plot(_frame):
    global spectrogram_data

    latest_column = None

    # Process all available microphone blocks.
    while True:
        try:
            block = audio_queue.get_nowait()
        except queue.Empty:
            break

        latest_column = compute_fft(block)

    if latest_column is not None:
        spectrogram_data[:, :-1] = spectrogram_data[:, 1:]
        spectrogram_data[:, -1] = latest_column

        image.set_data(spectrogram_data)

    return (image,)


# -----------------------------
# Start audio stream and plot
# -----------------------------
print("Available audio devices:")
print(sd.query_devices())
print("\nStarting microphone capture and repeating sweep.")
print("Close the plot window or press Ctrl+C to stop.")

fig, ax = plt.subplots(figsize=(11, 6))

image = ax.imshow(
    spectrogram_data,
    origin="lower",
    aspect="auto",
    interpolation="nearest",
    extent=[
        -DISPLAY_SECONDS,
        0,
        DISPLAY_MIN_FREQUENCY,
        DISPLAY_MAX_FREQUENCY,
    ],
    cmap="magma",
    vmin=-90,
    vmax=-20,
)

ax.set_title("Live Microphone FFT Spectrogram")
ax.set_xlabel("Time relative to now (seconds)")
ax.set_ylabel("Frequency (Hz)")

colorbar = fig.colorbar(image, ax=ax)
colorbar.set_label("Magnitude (dB)")

# Open the audio input and output stream and 
# attach our audio_callback
stream = sd.Stream(
    samplerate=SAMPLE_RATE,
    blocksize=BLOCK_SIZE,
    dtype="float32",
    channels=(CHANNELS, CHANNELS),
    device=(INPUT_DEVICE, OUTPUT_DEVICE),
    callback=audio_callback,
    latency="low",
)

# Open stream and run animation to update plot
try:
    with stream:
        animation = FuncAnimation(
            fig,
            update_plot,
            interval=50,
            blit=True,
            cache_frame_data=False,
        )

        plt.show()

except KeyboardInterrupt:
    pass

finally:
    plt.close(fig)
    print("Stopped.")
