'''
A simple script to play a tone on your speakers using sounddevice
'''

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44_100
DURATION = 3
FREQUENCY = 1000
AMPLITUDE = 0.2

t = np.arange(int(SAMPLE_RATE * DURATION)) / SAMPLE_RATE
tone = AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)

print(sd.query_devices())

# Replace this with the output device ID from the printed list.
OUTPUT_DEVICE = None

sd.play(
    tone.astype(np.float32),
    samplerate=SAMPLE_RATE,
    device=OUTPUT_DEVICE,
    blocking=True,
)
