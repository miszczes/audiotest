import scipy.io.wavfile as wavfile
import scipy
import scipy.fftpack as fftpk
import numpy as np
from matplotlib import pyplot as plt


def dbfft(x, fs, win=None, ref=32768):
    """
    Calculate spectrum in dB scale
    Args:
        x: input signal
        fs: sampling frequency
        win: vector containing window samples (same length as x).
             If not provided, then rectangular window is used by default.
        ref: reference value used for dBFS scale. 32768 for int16 and 1 for float
    Returns:
        freq: frequency vector
        s_db: spectrum in dB scale
    """
    N = len(x)  # Length of input sequence
    if win is None:
        win = np.ones(N)
    if len(x) != len(win):
        raise ValueError("Signal and window must be of the same length")
    x = x * win
    # Calculate real FFT and frequency vector
    sp = np.fft.rfft(x)
    freq = np.arange((N / 2) + 1) / (float(N) / fs)

    # Scale the magnitude of FFT by window and factor of 2,
    # because we are using half of FFT spectrum.
    s_mag = np.abs(sp) * 2 / np.sum(win)

    # Convert to dBFS
    s_dbfs = 20 * np.log10((s_mag / ref) / 20 * 10**-6)

    if len(freq) > len(s_dbfs):
        freq = freq[: len(s_dbfs)]
    if len(s_dbfs) > len(freq):
        s_dbfs = s_dbfs[: len(freq)]

    return freq, s_dbfs


def show_spectrum(data: str):
    s_rate, signal = wavfile.read(data)
    print(f"Czestotliwosc probkowania: {s_rate} Hz")
    l_audio = len(signal.shape)
    print(f"Ilosc kanalow: {l_audio}")
    if l_audio == 2:
        signal = signal.sum(axis=1) / 2
    N = signal.shape[0]
    print(f"Ilosc probek N: {N}")
    secs = N / float(s_rate)
    print(f"Czas trwania: {secs}s")
    Ts = 1.0 / s_rate  # sampling interval in time
    print(f"Okres T pomiedzy kolejnymi probkami: {Ts}s")

    freqs, FFT = dbfft(signal, s_rate)

    plt.xscale("log")
    plt.plot(freqs[range(100, len(freqs))], FFT[range(100, len(FFT))])
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude [dB]")
    plt.grid(True)
    plt.show()
