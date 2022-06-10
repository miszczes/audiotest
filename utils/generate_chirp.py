import numpy as np
from scipy.io import wavfile

samplerate = 44100
length = 10
chirplength = 10

f0 = 20
f1 = 20000

signal = np.arange(chirplength*samplerate)/(chirplength*samplerate)
signal = np.interp(signal, [0, 1], [f0, f1])
signal = np.append(signal, np.repeat(f1, (length-chirplength)*samplerate))
signal = np.sin(signal.cumsum() * 2 * np.pi / samplerate)
signal = np.float32(signal)
wavfile.write("chirp.wav", samplerate, signal)