import scipy.io.wavfile as wavfile
import numpy as np
from matplotlib import pyplot as plt
import datetime

def amplify(data):
    for i in range(len(data)):
        data[i] += 140
    return data

def get_max_chirp_val(data: str):
    s_rate, signal = wavfile.read(data)
    freqs, FFT = dbfft(signal, s_rate)
    #FFT = amplify(FFT)
    return max(FFT)

def interrupt_check(FFT, low_idx, data: str):
    for element in low_idx:
        if FFT[element] >= get_max_chirp_val(data):
            return 0


def zero(n):
    zero_array = []
    for _ in n:
        zero_array.append(1)
    return zero_array



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
    s_dbfs = 20 * np.log10((s_mag / ref))

    if len(freq) > len(s_dbfs):
        freq = freq[: len(s_dbfs)]
    if len(s_dbfs) > len(freq):
        s_dbfs = s_dbfs[: len(freq)]

    return freq, s_dbfs

def hl_envelopes_idx(s, dmin=1, dmax=1, split=False):
    """
    Input :
    s: 1d-array, data signal from which to extract high and low envelopes
    dmin, dmax: int, optional, size of chunks, use this if the size of the input signal is too big
    split: bool, optional, if True, split the signal in half along its mean, might help to generate the envelope in some cases
    Output :
    lmin,lmax : high/low envelope idx of input signal s
    """

    # locals min      
    lmin = (np.diff(np.sign(np.diff(s))) > 0).nonzero()[0] + 1 
    # locals max
    lmax = (np.diff(np.sign(np.diff(s))) < 0).nonzero()[0] + 1 
    

    if split:
        # s_mid is zero if s centered around x-axis or more generally mean of signal
        s_mid = np.mean(s) 
        # pre-sorting of locals min based on relative position with respect to s_mid 
        lmin = lmin[s[lmin]<s_mid]
        # pre-sorting of local max based on relative position with respect to s_mid 
        lmax = lmax[s[lmax]>s_mid]


    # global max of dmax-chunks of locals max 
    lmin = lmin[[i+np.argmin(s[lmin[i:i+dmin]]) for i in range(0,len(lmin),dmin)]]
    # global min of dmin-chunks of locals min 
    lmax = lmax[[i+np.argmax(s[lmax[i:i+dmax]]) for i in range(0,len(lmax),dmax)]]
    
    return lmin,lmax


def get_spectrum(data: str, output: str):
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
    #FFT = amplify(FFT)
    high_idx, low_idx = hl_envelopes_idx(FFT, dmax = 100, split=True)

    if interrupt_check(FFT, low_idx, "chirp.wav") == 0:
        plt.plot(zero(low_idx), FFT[low_idx], 'r')
        plt.xlabel("Bledny pomiar")
        plt.ylabel("Bledny pomiar")
        output = "plots/blad-zaklocenia_podczas_pomiaru_"+str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))+".png"
        plt.savefig(output)
    else:
        plt.plot(freqs[low_idx], FFT[low_idx],'g')
        plt.xscale("log")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Amplitude [dB]")
        plt.grid(True, which = "both")
        #plt.show()
        plt.savefig(output)
