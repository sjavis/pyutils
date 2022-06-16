#!/usr/bin/env python3

def progress(i, n, length=30):
    try: n = len(n)
    except TypeError: pass
    prog = i / (n - 1)
    filled = "="*int(prog*length)
    print('\r', f'[{filled:{length}}] {100*prog:.1f}%', end='')
    if (prog == 1):
        print()
