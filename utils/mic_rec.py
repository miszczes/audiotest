import argparse
import datetime

import sounddevice as sd
import numpy
assert numpy

import sys 
sys.path.append("C:/Users/miszczes/Desktop/audiotest/utils") 
from spectrum import get_spectrum


def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text


file_name = (
    "nagranie_" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".wav"
)
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true", help="wypisz urzadzenia audio"
)
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser],
)
parser.add_argument(
    "filename",
    nargs="?",
    type=str,
    default=file_name,
    metavar="FILENAME",
    help="nazwa pliku audio który ma byc nagrany",
)
parser.add_argument(
    "-d",
    "--device",
    type=int_or_str,
    help="urzadzenie wyjsciowe (numeryczne ID, badz string)",
)
parser.add_argument(
    "-r", "--samplerate", type=int, default=44100, help="czestotliwosc probkowania"
)
parser.add_argument("-c", "--channels", type=int, default=1, help="ilosc kanalow")
parser.add_argument("-t", "--subtype", type=str, help='typ nagrania (np. "PCM_24")')
parser.add_argument(
    "-D",
    "--duration",
    type=int,
    default=3,
    help="dlugosc trwania nagrywania, domyslnie 3s",
)
args = parser.parse_args(remaining)

from scipy.io.wavfile import write
print("Badanie rozpoczyna sie, prosze zachowac cisze!")
myrecording = sd.rec(
    args.duration * args.samplerate,
    samplerate=args.samplerate,
    channels=args.channels,
    device=args.device,
)
sd.wait()  # Wait until recording is finished
write("recordings/" + args.filename, args.samplerate, myrecording)  # Save as WAV file

print(f"Badanie zakonczone.\nPlik znajduje sie w recordings/{args.filename}")
get_spectrum("recordings/" + args.filename, "plots/"+args.filename+".png")

def get_file_name():
    file_name = "plots/"+args.filename+".png"
    return file_name

#parser.exit()