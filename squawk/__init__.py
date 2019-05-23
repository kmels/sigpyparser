import argparse
from vlc import squawk, play_on_windows
from signal_parser import parseSignal, Signal

def drive():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-s', '--signal')

    args = parser.parse_args()
    print(args.signal)
    if args.signal:
        sig = parseSignal(args.signal)
        squawk(sig)
    if args.file:
        play_on_windows(args.file)

if __name__ == '__main__':
    drive()
