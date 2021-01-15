#!/usr/bin/env python

import zipfile
import sys
from pathlib import Path

def unzipper(zdir, encoding, v):
    ''' Unzipping function accounting for variable
        encoding character types.
        Source: https://gist.github.com/hideaki-t/c42a16189dd5f88a955d
    '''
    with zipfile.ZipFile(zdir) as z:
        for i in z.namelist():
            n = Path(i.encode('cp437').decode(encoding))
            if v:
                print(n)
            if i[-1] == '/':
                if not n.exists():
                    n.mkdir()
            else:
                with n.open('wb') as w:
                    w.write(z.read(i))

if __name__ == '__main__':
    for i in sys.argv[1:]:
        unzip(i, 'cp932', 1)
