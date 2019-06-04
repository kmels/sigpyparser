import argparse
import os
from signal_parser import Signal
# Windows
def play_on_windows(*args):
    squawk = 'C:\\Program Files (x86)\VideoLAN\\VLC\\vlc.exe'
    files = ' '.join(list(args))
    command = f'"{squawk}" {files} --play-and-exit'
    print(command)
    os.system(command)
def play_on_unix(*args):
    squawk = 'play'
    files = ' '.join(list(args))
    command = f'{squawk} {files}'
    print(command)
    os.system(command)
    
def read_pips(p: int) -> list:
    return read_price(f"0.{p}")

def read_multiple(n:int):
    multiple = str()

def read_price(p: float) -> str:
    _int = int(p)
    _dec = round(p - _int,5)
    assert _dec < 1
    fs = []

    if _int >= 100:
        multiple = f'Lucy/Lucy_{_int // 100}.wav'
        hundred = 'Lucy/Lucy_100.wav'
        fs.extend([multiple,hundred])
        _int -= 100

        if _int > 0:
            fs.append('Lucy/Lucy_and.wav')

    def sub_hundred(_int):
        print("Sub hundred: ", _int)
        if _int == 0:
            fs.append(f'Lucy/Lucy_{_int}.wav')
            fs.append(f'Lucy/Lucy_{_int}.wav')
        elif _int < 20:
            fs.append(f'Lucy/Lucy_{_int}.wav')
        else:
            multiple = (_int // 10)*10
            fs.append(f'Lucy/Lucy_{multiple}.wav')

            if _int % multiple >= 1:
                fs.append(f'Lucy/Lucy_{_int % multiple}.wav')
    sub_hundred(_int)

    print("_dec:",_dec)
    if _dec != 0.0:
        #fs.append('Lucy/Lucy_dot.wav')
        if ("%.5f" % _dec).endswith('000'):
            pip_digits = f"%.2f" % _dec
        else:
            pip_digits = f"%.4f" % _dec
            
        pips = pip_digits.split(".")[-1]
        print(pips, ".. ",len(pips))

        assert len(pips) < 5

        if len(pips) < 2:
            sub_hundred(int(pips))
            fs.append('Lucy/Lucy_Cents.wav')
        else:
            sub_hundred(int(pips[0:2]))
            sub_hundred(int(pips[2:4]))
            #fs.append('Lucy/Lucy_Pips.wav')

    return ' '.join(fs)

def squawk(sig: Signal):
    assert type(sig) is Signal

    if os.name == 'nt':
        pair = f'Rachel/Rachel_{sig["pair"]}.wav'
        print(sig)
        sign = f'Rachel/Rachel_{sig["sign"]}.wav'

        price = read_price(sig["entry"])
        
        play_on_windows(pair,sign, price)
    else:

        pair = f'Rachel/Rachel_{sig["pair"]}.wav'
        sign = f'Rachel/Rachel_{sig["sign"]}.wav'
        price = read_price(sig["entry"])

        print(pair,sign,pair)
        play_on_unix(pair, sign, price)
