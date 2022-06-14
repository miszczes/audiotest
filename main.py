import subprocess
import threading
import time
import scipy.io.wavfile as wavfile
import os

from tkinter import *
from PIL import ImageTk, Image

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
    footer.place(anchor='s', relx=0.5, rely=1)
    change_textlabel(footer_text, f"Czas trwania: {secs} s\nIlosc probek N: {N}\nIlosc kanalow: {l_audio}\nCzestotliwosc probkowania: {s_rate} Hz\nOkres T pomiedzy kolejnymi probkami: {Ts} s")

def recording(length: str):
    cmd_rec = ["python", "utils/mic_rec.py", "-D", length]
    subprocess.run(cmd_rec)

def playback(filename: str):
    cmd_play = ["python", "utils/playback.py", filename]
    subprocess.run(cmd_play)

def init_test(timeout: int, filename: str):
    print(f"Badanie rozpocznie sie za {timeout} s")
    change_textlabel(my_string, f"Badanie rozpocznie sie za {timeout} s")
    for i in range(timeout):
        print(f"{i+1}...")
        change_textlabel(my_string, f"{i+1}...")
        time.sleep(1)
    print("Standby...")
    change_textlabel(my_string, "Badanie rozpoczete, prosze zachowac cisze!")
    thread1 = threading.Thread(recording(str(return_length(filename))))
    thread2 = threading.Thread(playback(filename))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    recnames = os.listdir("recordings/")
    get_filevalues("recordings/"+recnames[-1])
def click_action(button):
    button.pack_forget()
    root_tk.update()
    init_test(5, "chirp.wav")
    plotnames = os.listdir("plots/")
    frame = Frame(root_tk, width=600, height=400)
    frame.pack()
    frame.place(anchor='center', relx=0.5, rely=0.5)

    img = ImageTk.PhotoImage(Image.open("plots/"+plotnames[-1]))

    label = Label(frame, image = img)
    label.pack()
    button.config(text=f"Wykonaj Badanie Ponownie!")
    button.pack()
    root_tk.update()
    my_string.set(f"Badanie zakonczone! Wynik znajduje sie w\nplots/{plotnames[-1]}")
    Tk.update(self=None)

def create_command(func, *args, **kwargs):
    def command():
        return func(*args, **kwargs)
    return command

root_tk = Tk()
root_tk.geometry("800x800")
root_tk.title("AudioTest")
click_button = Button(root_tk, text="Wykonaj Badanie Głośnika!")
my_string = StringVar()
footer_text = StringVar()
label = Label(root_tk, textvariable=my_string)
footer = Label(root_tk, textvariable=footer_text)
click_button.pack()
label.pack()
footer.pack()
click_button.config(command=create_command(click_action, click_button))
root_tk.mainloop()
