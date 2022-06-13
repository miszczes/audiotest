import scipy.io.wavfile as wavfile
import scipy
import scipy.fftpack as fftpk
import numpy as np
from matplotlib import pyplot as plt

def show_spectrum(data: str):
    s_rate, signal = wavfile.read(data) 
    print (f"Czestotliwosc probkowania: {s_rate} Hz")
    l_audio = len(signal.shape)
    print (f"Ilosc kanalow: {l_audio}")
    if l_audio == 2:
        signal = signal.sum(axis=1) / 2
    N = signal.shape[0]
    print (f"Ilosc probek N: {N}")
    secs = N / float(s_rate)
    print (f"Czas trwania: {secs}s")
    Ts = 1.0/s_rate # sampling interval in time
    print (f"Okres T pomiedzy kolejnymi probkami: {Ts}s")

    FFT = abs(scipy.fft.fft(signal))
    freqs = fftpk.fftfreq(len(FFT), (1.0/s_rate))

    plt.xscale("log")
    plt.plot(freqs[range(100, len(FFT)//2)], FFT[range(100, len(FFT)//2)])                                                          
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.show()