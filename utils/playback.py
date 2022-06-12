import argparse
import threading

import sounddevice as sd
import soundfile as sf


def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='wypisz urzadzenia audio')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'filename', metavar='FILENAME',
    help='nazwa pliku audio który ma byc nagrany')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='rzadzenie wyjsciowe (numeryczne ID, badz string)')
args = parser.parse_args(remaining)

event = threading.Event()

try:
    data, fs = sf.read(args.filename, always_2d=True)

    current_frame = 0

    def callback(outdata, frames, time, status):
        global current_frame
        if status:
            print(status)
        chunksize = min(len(data) - current_frame, frames)
        outdata[:chunksize] = data[current_frame:current_frame + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop()
        current_frame += chunksize

    stream = sd.OutputStream(
        samplerate=fs, device=args.device, channels=data.shape[1],
        callback=callback, finished_callback=event.set)
    with stream:
        event.wait()  # Wait until playback is finished
except KeyboardInterrupt:
    parser.exit('\nPrzerwano przez uzytkownika')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))