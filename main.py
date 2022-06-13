import subprocess
import threading
import time
import scipy.io.wavfile as wavfile
import sys


import py_compile

py_compile.compile("utils/playback.py")
py_compile.compile("utils/mic_rec.py")

global file_name


def return_length(filename: str):
    s_rate, signal = wavfile.read(filename)
    N = signal.shape[0]
    secs = N / float(s_rate)
    return int(secs)


def recording(length: str):
    cmd_rec = ["python", "utils/mic_rec.py", "-D", length]
    subprocess.run(cmd_rec)


def playback(filename: str):
    cmd_play = ["python", "utils/playback.py", filename]
    subprocess.run(cmd_play)


def init_test(timeout: int, filename: str):
    print(f"Badanie rozpocznie sie za {timeout} s")
    for i in range(timeout):
        print(f"{i+1}...")
        time.sleep(1)
    print("Badanie rozpoczyna sie, prosze zachowac cisze\nStandby...")
    thread1 = threading.Thread(recording(str(return_length(filename))))
    thread2 = threading.Thread(playback(filename))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


init_test(5, "chirp.wav")
