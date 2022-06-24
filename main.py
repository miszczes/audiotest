import subprocess
import threading
import time, datetime
import scipy.io.wavfile as wavfile
import os, glob

import sounddevice as sd
import soundfile as sf

from utils.spectrum import get_spectrum

from tkinter import *
from PIL import ImageTk, Image


def filter_devices(in_out: str):
    devices = []
    host_apis = []
    inout_devices = []
    inout_ = []
    for dict in sd.query_devices():
        for key, value in dict.items():
            if (key == in_out) and value > 0:
                devices.append(dict)
    for dictio in devices:
        for key, value in dictio.items():
            if key == "hostapi":
                host_apis.append(sd.query_hostapis()[value])
    for dictio in devices:
        for key, value in dictio.items():
            if key == "name":
                inout_devices.append(value)
    for i in range(len(host_apis)):
        inout_.append(inout_devices[i] + ", " + host_apis[i]["name"])
    return inout_


def change_textlabel(mystring, text: str):
    mystring.set(text)
    root_tk.update()


def return_length(filename: str):
    s_rate, signal = wavfile.read(filename)
    N = signal.shape[0]
    secs = N / float(s_rate)
    return int(secs)


def get_filevalues(data: str):
    s_rate, signal = wavfile.read(data)
    l_audio = len(signal.shape)
    if l_audio == 2:
        signal = signal.sum(axis=1) / 2
    N = signal.shape[0]
    secs = N / float(s_rate)
    Ts = 1.0 / s_rate
    footer.place(anchor="s", relx=0.5, rely=1)
    change_textlabel(
        footer_text,
        f"Czas trwania: {secs} s\nIlosc probek N: {N}\nIlosc kanalow: {l_audio}\nCzestotliwosc probkowania: {s_rate} Hz\nOkres T pomiedzy kolejnymi probkami: {Ts} s",
    )


def recording(length: int, sample_rate, chann, device: str):
    # cmd_rec = ["python", "utils/mic_rec.py", "-D", length, "-d", device]
    # subprocess.run(cmd_rec)

    file_name = (
        "nagranie_"
        + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        + ".wav"
    )
    from scipy.io.wavfile import write

    print("Badanie rozpoczyna sie, prosze zachowac cisze!")
    myrecording = sd.rec(
        length * sample_rate,
        samplerate=sample_rate,
        channels=chann,
        device=device,
    )
    sd.wait()  # Wait until recording is finished
    write("recordings/" + file_name, sample_rate, myrecording)  # Save as WAV file
    print(f"Badanie zakonczone.\nPlik znajduje sie w recordings/{file_name}")
    get_spectrum("recordings/" + file_name, "plots/" + file_name + ".png")
    print("zakonczenie nagrywania")


def playback(filename: str, device: str):
    # cmd_play = ["python", "utils/playback.py", filename, "-d", device]
    # subprocess.run(cmd_play)

    file_name = (
        "nagranie_"
        + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        + ".wav"
    )
    print("rozpoczecie playbacku")
    from scipy.io.wavfile import read

    samplerate, wavarray = read(filename)
    sd.default.samplerate = samplerate
    sd.default.device = device
    sd.play(wavarray)
    sd.wait()  # wait until playback is finished
    print("zakonczenie playbacku")


def init_test(timeout: int, filename: str):
    print(f"Badanie rozpocznie sie za {timeout} s")
    change_textlabel(my_string, f"Badanie rozpocznie sie za {timeout} s")
    for i in range(timeout):
        print(f"{i+1}...")
        change_textlabel(my_string, f"{i+1}...")
        time.sleep(1)
    print("Standby...")
    change_textlabel(my_string, "Badanie rozpoczete, prosze zachowac cisze!")
    in_ = in_variable.get()
    out_ = out_variable.get()
    length = return_length(filename)

    thread1 = threading.Thread(
        target=recording,
        args=(
            length,
            44100,
            2,
            in_,
        ),
    )
    thread2 = threading.Thread(
        target=playback,
        args=(
            filename,
            out_,
        ),
    )

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


def click_action(button):
    button.pack_forget()  # przycisk znika
    in_drop.pack_forget()  # menu rozwijane znika
    out_drop.pack_forget()
    root_tk.update()
    init_test(5, "chirp.wav")  # rozpoczyna sie badanie
    plotnames = glob.glob(os.getcwd() + "/plots/*.png")
    latest_file = max(plotnames, key=os.path.getctime)
    if "blad" in latest_file:  # wyswietlenie wynikow
        root_tk.geometry("250x250")
        my_string.set("Bledny pomiar:\n zaklocenia podczas pomiaru!")
        button.config(text=f"Wykonaj Badanie Ponownie!")
        in_drop.pack()
        button.pack()
        out_drop.pack()
        root_tk.update()
    else:
        root_tk.geometry("800x800")
        frame = Frame(root_tk, width=600, height=400)
        frame.pack()
        frame.place(anchor="center", relx=0.5, rely=0.5)
        img = ImageTk.PhotoImage(Image.open(latest_file))
        label = Label(frame, image=img)
        in_drop.pack()
        button.pack()
        out_drop.pack()
        label.pack()
        button.config(text=f"Wykonaj Badanie Ponownie!")
        root_tk.update()
        my_string.set(f"Badanie zakonczone! Wynik znajduje sie w\n{latest_file}")
        recnames = os.listdir("recordings/")
        get_filevalues("recordings/" + recnames[-1])
    Tk.update(self=None)


def create_command(func, *args, **kwargs):
    def command():
        return func(*args, **kwargs)

    return command


root_tk = Tk()
root_tk.geometry("250x100")
root_tk.title("AudioTest")
click_button = Button(root_tk, text="Wykonaj Badanie Głośnika!")
my_string = StringVar()
footer_text = StringVar()
label = Label(root_tk, textvariable=my_string)
footer = Label(root_tk, textvariable=footer_text)
in_variable = StringVar(root_tk)
in_variable.set(sd.query_devices(kind="input")["name"])  # default value
out_variable = StringVar(root_tk)
out_variable.set(sd.query_devices(kind="output")["name"])  # default value
in_devices = filter_devices("max_input_channels")
out_devices = filter_devices("max_output_channels")
in_drop = OptionMenu(root_tk, in_variable, *in_devices)
out_drop = OptionMenu(root_tk, out_variable, *out_devices)
in_drop.place(anchor="nw")
in_drop.pack()
click_button.pack()
out_drop.pack()
label.pack()
footer.pack()
click_button.config(command=create_command(click_action, click_button))
root_tk.mainloop()
