#!/usr/bin/env python3

def progress(i, n, length=30):
    # Get length if iterable has been passed
    try: n = len(n)
    except TypeError: pass
    # Ensure i and n are valid
    assert isinstance(n, int)
    assert (n > 0)
    assert (i >= 0)
    assert (i <= n-1)
    # Prevent divide by zero for length 1
    if (n == 1):
        i = 1
        n = 2
    # Output
    prog = i / (n - 1)
    filled = "="*int(prog*length)
    print('\r', f'[{filled:{length}}] {100*prog:.1f}%', end='')
    if (prog == 1):
        print()
